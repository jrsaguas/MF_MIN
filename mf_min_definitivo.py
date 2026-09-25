"""
================================================================================
MF_MIN — Núcleo Formal Mínimo  ⟨O, M, A, δ⟩
VERSIÓN DEFINITIVA — fusión verificada de dos líneas de desarrollo independientes
================================================================================

Este archivo fusiona dos versiones de MF_MIN que llegaron a la auditoría de
cierre por caminos separados:

  (1) Una versión previa (Claude) que corrigió los 10 puntos de una auditoría
      externa: bug de IDs en saturate(), autorrepresentación formal (F1) sin
      función Python externa, honestidad sobre "independencia operacional"
      vs. irreductibilidad, dominio restringido de freeze_value(), rollback
      ante contradicción semántica y ante invalidación por axioma nuevo,
      verificación real de justificación de derivaciones (verify_derivation),
      y prueba formal de ~π como relación de equivalencia.

  (2) Una versión posterior (ChatGPT + Qwen), desarrollada de forma
      independiente sobre el resultado de (1), con una batería propia de 61
      pruebas y varias validaciones estructurales más estrictas: cadenas no
      vacías en todos los campos identificadores, acoplamiento origin/rule_id,
      integridad referencial de premises como invariante de Kernel (no solo
      de auditoría externa), prohibición de eliminar una relación citada como
      premisa, rechazo de variables de conclusión no ligadas en Rule,
      restricciones de batch_derive (sin dependencias internas, sin origin
      distinto de "derived"), validación de que los propios límites
      numéricos de un axioma sean finitos, e integridad referencial de
      constantes dentro de cláusulas axiomáticas.

NO se fusionó por lectura ni por argumento de autoridad: se sometieron ambas
versiones a una batería de pruebas cruzadas adversariales (mismo escenario,
ejecutado contra las dos implementaciones) para encontrar diferencias de
comportamiento reales. Resultado de esa comparación:

  Defectos reales encontrados en (1), corregidos aquí adoptando la solución
  de (2):
    - _satisfies_clauses trataba las cláusulas '__distinct__' en el mismo
      bucle lineal que las relacionales: si '__distinct__' aparecía ANTES de
      la cláusula que liga sus variables, el axioma nunca disparaba —
      confirmado empíricamente. La versión (2) separa la unificación
      relacional (siempre completa primero) de las restricciones
      '__distinct__' (aplicadas después, sobre cada binding sobreviviente),
      lo que hace el resultado independiente del orden textual del body.
    - No prohibía eliminar una relación citada como premisa de otra
      (quedaba huérfana). Corregido: remove_relation ahora lo rechaza.
    - Rule no rechazaba variables de conclusión no ligadas por ninguna
      premisa; Relation/Object/Clause no rechazaban cadenas vacías; nada
      exigía que las premisas referenciadas EXISTIERAN como invariante de
      Kernel (solo se auditaba después, con verify_derivation). Las cuatro
      correcciones se adoptan de (2).

  Defectos reales encontrados en (2), corregidos aquí adoptando la solución
  de (1):
    - No existía invariante alguna que impidiera que dos identificadores
      distintos afirmaran EXACTAMENTE el mismo hecho (source, predicate,
      target, polarity) — confirmado: se pudo duplicar un hecho sin que el
      Kernel protestara. Se reincorpora la invariante I4 (unicidad
      semántica de hechos) de (1).
    - No existía ningún mecanismo — ni a nivel Kernel, ni de auditoría — que
      detectara una relación derivada "forjada" (rule_id y premises reales,
      pero cuya conclusión NO es lo que esa regla+esas premisas producirían
      realmente). Confirmado con un caso limpio (sin colisión con I4). Se
      reincorpora EngineD.verify_derivation de (1).
    - La prueba F1 de (2) no reconstruye el escenario original de
      autorrepresentación formal (completitud de las 4 primitivas detectada
      DENTRO del formalismo, vía negación explícita + axioma con variable
      compartida, sin función Python externa). Se confirmó que el motor de
      cláusulas de (2) SÍ soporta ese escenario exacto — simplemente no
      estaba probado. Se añade como F2, usando la versión original de (1).
    - project_pi() no tenía una función states_equivalent() nombrada, ni se
      probaba que ~π fuera efectivamente una relación de equivalencia
      (reflexiva, simétrica, transitiva) con poder discriminante real. Se
      añade, de (1).
    - No había ninguna prueba explícita de que CONTRADICTION sea
      inalcanzable a través de δ (aunque el docstring de query_evidence lo
      declaraba). Se añade, de (1).
    - G1-G5 se presentaban como "invariantes operacionales" sin distinguir
      eso de irreductibilidad matemática. Se añade la distinción explícita
      y un argumento de irreductibilidad genuina pero acotado (solo para O),
      de (1).

  Confirmado que AMBAS versiones resuelven correctamente, por caminos
  distintos, el defecto original más grave (colisión de IDs cuando dos
  reglas concluyen el mismo hecho en la misma ronda de saturate()): se
  ejecutó el mismo escenario contra las dos y ambas lo manejan bien. Se
  conserva el mecanismo de (2) (ID determinista por hash + deduplicación
  semántica post-hoc en saturate()) por ser igual de correcto y más simple.

Este archivo mantiene el nombre de todas las clases y la mayoría de las
pruebas existentes de (2) sin modificarlas (ya estaban verificadas), y
añade las piezas de (1) que le faltaban, cada una con su propia prueba
nueva en la batería de cierre.
================================================================================
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import threading
from collections.abc import Mapping
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Dict, List, Optional, Set, Tuple


# ============================================================
# CAPA 0 — ERRORES FORMALES
# ============================================================

class KernelError(Exception):
    pass


class ValidationError(KernelError):
    pass


class DuplicateIDError(ValidationError):
    pass


class MissingReferenceError(ValidationError):
    pass


class InvalidTransitionError(ValidationError):
    pass


class ContradictionError(ValidationError):
    pass


class DuplicateFactError(ValidationError):
    """
    I4 — Unicidad semántica de hechos (reincorporada tras pruebas cruzadas).
    Dos identificadores distintos no pueden afirmar el mismo triple
    (source, predicate, target) en la misma polaridad. Sin esta invariante,
    M puede acumular redundancia silenciosa: el mismo hecho, representado
    dos veces con IDs distintos, sin que ninguna otra capa lo detecte.
    """
    pass


# ============================================================
# CAPA 1 — MF_MIN = <O, M, A, δ>
# ============================================================

IMMUTABLE_SCALARS = (
    int,
    float,
    str,
    bool,
    type(None),
)


def freeze_value(value: Any) -> Any:
    """
    Normalizador/congelador de valores pertenecientes al dominio de datos
    admitido por MF_MIN. No es un congelador universal de Python.
    
    Contrato: Object.value es un dato general; los axiomas numéricos
    determinan cuándo ese dato debe ser numérico.
    """
    if isinstance(value, Mapping):
        return MappingProxyType({
            freeze_value(k): freeze_value(v)
            for k, v in value.items()
        })

    if isinstance(value, (list, tuple)):
        return tuple(
            freeze_value(v)
            for v in value
        )

    if isinstance(value, (set, frozenset)):
        return frozenset(
            freeze_value(v)
            for v in value
        )

    if isinstance(value, IMMUTABLE_SCALARS):
        return value

    raise TypeError(
        f"Tipo no soportado para congelamiento: "
        f"{type(value).__name__}"
    )


def freeze_entity_mapping(
    value: Mapping[str, Any],
    expected_type: type,
    name: str,
) -> Mapping[str, Any]:

    if not isinstance(value, Mapping):
        raise ValidationError(
            f"{name} debe ser Mapping."
        )

    result = dict(value)

    for key, entity in result.items():
        if not isinstance(key, str) or not key:
            raise ValidationError(
                f"{name}: las claves deben ser strings no vacíos."
            )

        if not isinstance(entity, expected_type):
            raise ValidationError(
                f"{name}: entidad inválida para '{key}'."
            )

        if entity.id != key:
            raise ValidationError(
                f"{name}: key='{key}' != id='{entity.id}'."
            )

    return MappingProxyType(result)


def require_nonempty_string(
    value: Any,
    field_name: str,
) -> None:
    if not isinstance(value, str) or not value:
        raise ValidationError(
            f"{field_name} debe ser una cadena no vacía."
        )


def require_finite_number(
    value: Any,
    field_name: str,
) -> None:
    """Valida que un valor sea numérico y finito (no NaN ni Inf)."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValidationError(f"{field_name} debe ser numérico.")
    if not math.isfinite(float(value)):
        raise ValidationError(f"{field_name} debe ser finito (no NaN ni Inf).")


def require_payload_fields(
    payload: Mapping[str, Any],
    *fields: str,
) -> None:
    """Verifica que un payload contenga todos los campos obligatorios."""
    for f in fields:
        if f not in payload:
            raise ValidationError(
                f"Payload incompleto: falta '{f}'."
            )


# ============================================================
# O — OBJETOS
# ============================================================

@dataclass(frozen=True)
class Object:
    """
    O: Entidad discreta inmutable con identidad única.
    La identidad está determinada por ID; igualdad de valor no implica identidad.
    
    Nota: Inmutabilidad estructural ≠ hashabilidad universal.
    MappingProxyType garantiza inmutabilidad superficial pero no convierte
    automáticamente toda la estructura en hashable.
    """
    id: str
    type: str
    value: Any = None
    properties: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        require_nonempty_string(self.id, "Object.id")
        require_nonempty_string(self.type, "Object.type")

        object.__setattr__(self, "value", freeze_value(self.value))
        object.__setattr__(self, "properties", freeze_value(self.properties))


# ============================================================
# M — RELACIONES
# ============================================================

@dataclass(frozen=True)
class Relation:
    """
    M: Relación dirigida inmutable con polaridad y procedencia.
    Una Relation derived requiere rule_id, pero premises puede estar vacío
    (permite reglas axiomáticas sin evidencia relacional explícita).
    
    Contrato: ID de relación ≠ identidad semántica de relación.
    M_operacional permite múltiples relaciones con misma semántica pero diferentes IDs.
    M_semántico (π_M) colapsa esas diferencias.
    
    Semántica de polarity:
    - polarity=True: evidencia positiva explícita (afirmación)
    - polarity=False: evidencia negativa explícita (negación explícita)
    NO es negación por ausencia. La ausencia de evidencia se representa mediante
    la no existencia de la relación (UNKNOWN en query_evidence).
    
    Procedencia (premises):
    Las premisas son referencias históricas a las evidencias utilizadas durante
    la derivación. No se impone restricción de aciclicidad (DAG) sobre el grafo
    de procedencia. Los ciclos son permitidos como referencias históricas.
    """
    id: str
    source: str
    predicate: str
    target: str
    polarity: bool = True
    origin: str = "asserted"
    rule_id: Optional[str] = None
    premises: Tuple[str, ...] = ()

    def __post_init__(self):
        for name, value in (
            ("Relation.id", self.id),
            ("Relation.source", self.source),
            ("Relation.predicate", self.predicate),
            ("Relation.target", self.target),
        ):
            require_nonempty_string(value, name)

        if not isinstance(self.polarity, bool):
            raise ValidationError("Relation.polarity debe ser bool.")

        if self.origin not in ("asserted", "derived", "proposed"):
            raise ValidationError("origin debe ser 'asserted', 'derived' o 'proposed'.")

        if self.origin == "derived":
            if not self.rule_id:
                raise ValidationError("Una Relation derived requiere rule_id.")
        elif self.rule_id is not None:
            raise ValidationError("Una Relation asserted no debe tener rule_id.")

        premises = tuple(self.premises)
        for premise in premises:
            require_nonempty_string(premise, "Relation.premises")

        object.__setattr__(self, "premises", premises)


# ============================================================
# A — CLÁUSULAS
# ============================================================

@dataclass(frozen=True)
class Clause:
    """
    Cláusula atómica para el cuerpo de restricciones axiomáticas.
    Si source/target no son variables (?X), deben referenciar objetos existentes en O.
    
    Nota: __distinct__ es un predicado reservado del metalenguaje del evaluador.
    No representa un predicado ordinario del dominio, sino un operador interno
    de comparación de identidad.
    
    Semántica de polarity en cláusulas:
    - polarity=True: busca relaciones con evidencia positiva
    - polarity=False: busca relaciones con evidencia negativa explícita
    NO es negación por ausencia.
    """
    predicate: str
    source: str
    target: str
    polarity: bool = True

    def __post_init__(self):
        require_nonempty_string(self.predicate, "Clause.predicate")
        require_nonempty_string(self.source, "Clause.source")
        require_nonempty_string(self.target, "Clause.target")

        if not isinstance(self.polarity, bool):
            raise ValidationError("Clause.polarity debe ser bool.")


# ============================================================
# A — AXIOMAS
# ============================================================

@dataclass(frozen=True)
class AxiomConstraint:
    """
    A: Restricción semántica declarativa prohibitiva.
    Representa invariantes de consistencia: ¬(C1 ∧ C2 ∧ ... ∧ Cn).
    Si el cuerpo (body) se satisface en el estado, el estado es inválido.
    
    A no es un lenguaje universal de axiomas matemáticos, sino un sistema
    mínimo de restricciones semánticas sobre estados estructurados.
    
    body=() indica que el componente relacional del axioma no contiene cláusulas
    y, por tanto, no activa restricciones basadas en cláusulas. El axioma puede
    seguir siendo activo mediante restricciones numéricas (min/max_numeric_val).
    
    Restricciones numéricas: numeric_target_type aplica a TODOS los objetos de ese tipo,
    no a un objeto específico. Es una restricción por tipo, no por instancia.
    """
    id: str
    name: str
    body: Tuple[Clause, ...] = ()
    min_numeric_val: Optional[float] = None
    max_numeric_val: Optional[float] = None
    numeric_target_type: Optional[str] = None

    def __post_init__(self):
        require_nonempty_string(self.id, "Axiom.id")
        require_nonempty_string(self.name, "Axiom.name")

        body = tuple(self.body)
        for clause in body:
            if not isinstance(clause, Clause):
                raise ValidationError("Axiom.body solo admite Clause.")

        # Validación estricta de límites numéricos
        if self.min_numeric_val is not None:
            require_finite_number(self.min_numeric_val, "Axiom.min_numeric_val")

        if self.max_numeric_val is not None:
            require_finite_number(self.max_numeric_val, "Axiom.max_numeric_val")

        if (
            self.min_numeric_val is not None
            and self.max_numeric_val is not None
            and self.min_numeric_val > self.max_numeric_val
        ):
            raise ValidationError("Rango numérico inválido.")

        object.__setattr__(self, "body", body)


# ============================================================
# ESTADO S = <O, M, A>
# ============================================================

@dataclass(frozen=True)
class State:
    """S = <O, M, A> Estado inmutable completo."""
    objects: Mapping[str, Object] = field(default_factory=dict)
    relations: Mapping[str, Relation] = field(default_factory=dict)
    axioms: Mapping[str, AxiomConstraint] = field(default_factory=dict)

    def __post_init__(self):
        object.__setattr__(self, "objects", freeze_entity_mapping(self.objects, Object, "State.objects"))
        object.__setattr__(self, "relations", freeze_entity_mapping(self.relations, Relation, "State.relations"))
        object.__setattr__(self, "axioms", freeze_entity_mapping(self.axioms, AxiomConstraint, "State.axioms"))


# ============================================================
# δ — TRANSICIÓN
# ============================================================

@dataclass(frozen=True)
class Transition:
    """t = (operación, payload) Transición atómica."""
    operation: str
    payload: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        require_nonempty_string(self.operation, "Transition.operation")
        object.__setattr__(self, "payload", freeze_value(self.payload))


# ============================================================
# EVALUADOR A
# ============================================================

class EvaluatorA:
    """Evaluador uniforme de consistencia sobre el estado."""

    def check_consistency(self, state: State) -> None:
        self._check_numeric_bounds(state)
        self._check_direct_contradictions(state)
        # Índice (predicate, polarity) -> [Relation], construido UNA VEZ por
        # transición y compartido entre todos los axiomas/cláusulas de esta
        # verificación (añadido tras medir, no suponer: sin esto,
        # _satisfies_clauses escaneaba state.relations completo por cada
        # cláusula de cada axioma, en CADA transición — no solo durante
        # derivación, a diferencia de EngineD, que ya tenía su propio índice
        # pero solo para su propio uso interno).
        index = _PredicatePolarityIndex(state)
        self._check_axiom_clauses(state, index)

    def _check_numeric_bounds(self, state: State) -> None:
        for axiom in state.axioms.values():
            if axiom.numeric_target_type is None:
                continue

            for obj in state.objects.values():
                if obj.type != axiom.numeric_target_type:
                    continue
                if obj.value is None:
                    continue

                if isinstance(obj.value, bool) or not isinstance(obj.value, (int, float)):
                    raise ContradictionError(f"Tipo numérico inválido en '{obj.id}'.")

                value = float(obj.value)
                if not math.isfinite(value):
                    raise ContradictionError(f"NaN/Inf en '{obj.id}'.")

                if axiom.min_numeric_val is not None and value < axiom.min_numeric_val:
                    raise ContradictionError(f"Axioma '{axiom.id}' violado.")

                if axiom.max_numeric_val is not None and value > axiom.max_numeric_val:
                    raise ContradictionError(f"Axioma '{axiom.id}' violado.")

    def _check_direct_contradictions(self, state: State) -> None:
        """
        Verifica dos invariantes en un solo recorrido:

        I3 — No-contradicción de polaridad: un triple (source, predicate,
        target) no puede estar afirmado en polaridad True y en polaridad
        False simultáneamente.

        I4 — Unicidad semántica de hechos (reincorporada tras pruebas
        cruzadas contra una versión que carecía de ella): un triple, en UNA
        polaridad dada, no puede estar respaldado por más de un
        identificador. Sin esto, dos IDs distintos pueden afirmar
        exactamente el mismo hecho sin que nada lo impida.
        """
        polarity_by_edge: Dict[Tuple[str, str, str], bool] = {}
        owner_by_edge_polarity: Dict[Tuple[str, str, str, bool], str] = {}

        for relation in state.relations.values():
            edge = (relation.source, relation.predicate, relation.target)
            previous = polarity_by_edge.get(edge)

            if previous is not None and previous != relation.polarity:
                raise ContradictionError(f"Contradicción directa (I3): {edge}")

            edge_pol = edge + (relation.polarity,)
            if edge_pol in owner_by_edge_polarity:
                raise DuplicateFactError(
                    f"Hecho duplicado (I4): '{owner_by_edge_polarity[edge_pol]}' y "
                    f"'{relation.id}' afirman el mismo triple {edge} en polaridad {relation.polarity}."
                )
            owner_by_edge_polarity[edge_pol] = relation.id
            polarity_by_edge[edge] = relation.polarity

    def _check_axiom_clauses(self, state: State, index: "_PredicatePolarityIndex") -> None:
        for axiom in state.axioms.values():
            if not axiom.body:
                continue

            if self._satisfies_clauses(axiom.body, index):
                raise ContradictionError(f"Axioma '{axiom.id}' ({axiom.name}) detonado.")

    def _satisfies_clauses(self, clauses: Tuple[Clause, ...], index: "_PredicatePolarityIndex") -> bool:
        relational = [c for c in clauses if c.predicate != "__distinct__"]
        constraints = [c for c in clauses if c.predicate == "__distinct__"]

        bindings: List[Dict[str, str]] = [{}]

        # UNIFICACIÓN RELACIONAL — antes escaneaba TODAS las relaciones del
        # estado por cada cláusula; ahora consulta solo las que comparten
        # (predicate, polarity) con la cláusula, vía el índice precomputado.
        for clause in relational:
            next_bindings = []
            for binding in bindings:
                for relation in index.by_predicate_polarity(clause.predicate, clause.polarity):
                    matched = self._match_clause(clause, relation, binding)
                    if matched is not None:
                        next_bindings.append(matched)

            bindings = next_bindings
            if not bindings:
                return False

        # RESTRICCIONES
        for binding in bindings:
            valid = True
            for clause in constraints:
                source = self._resolve_term(clause.source, binding)
                target = self._resolve_term(clause.target, binding)

                if source is None or target is None:
                    valid = False
                    break

                if clause.predicate == "__distinct__" and source == target:
                    valid = False
                    break

            if valid:
                return True

        return False

    @staticmethod
    def _resolve_term(term: str, binding: Dict[str, str]) -> Optional[str]:
        if term.startswith("?"):
            return binding.get(term)
        return term

    @staticmethod
    def _match_clause(clause: Clause, relation: Relation, binding: Dict[str, str]) -> Optional[Dict[str, str]]:
        result = dict(binding)

        for variable, value in (
            (clause.source, relation.source),
            (clause.target, relation.target),
        ):
            if variable.startswith("?"):
                if variable in result and result[variable] != value:
                    return None
                result[variable] = value
            elif variable != value:
                return None

        return result


class _PredicatePolarityIndex:
    """
    Índice de relaciones por (predicate, polarity), construido una vez por
    llamada a EvaluatorA.check_consistency() y reutilizado por TODOS los
    axiomas/cláusulas de esa verificación — en vez de que cada cláusula de
    cada axioma reescanee state.relations por su cuenta.

    Complejidad: construir el índice es O(relaciones), una sola vez. Cada
    consulta posterior es O(1) + O(tamaño del grupo), en vez de O(relaciones
    totales) sin importar el grupo. Con A axiomas y C cláusulas promedio por
    axioma, esto cambia el costo de una transición de O(A·C·|relaciones|) a
    O(|relaciones| + A·C·|grupo relevante|).
    """
    def __init__(self, state: State):
        self._by_pred_pol: Dict[Tuple[str, bool], List[Relation]] = {}
        for rel in state.relations.values():
            self._by_pred_pol.setdefault((rel.predicate, rel.polarity), []).append(rel)

    def by_predicate_polarity(self, predicate: str, polarity: bool) -> List[Relation]:
        return self._by_pred_pol.get((predicate, polarity), [])


# ============================================================
# VALIDATOR
# ============================================================

class Validator:
    """Validador estructural y semántico de invariantes."""

    def __init__(self):
        self.evaluator = EvaluatorA()

    def validate(self, state: State) -> None:
        # Integridad referencial de M
        for relation in state.relations.values():
            if relation.source not in state.objects:
                raise MissingReferenceError(f"Origen inexistente: {relation.source}")
            if relation.target not in state.objects:
                raise MissingReferenceError(f"Destino inexistente: {relation.target}")

            for premise in relation.premises:
                if premise not in state.relations:
                    raise MissingReferenceError(f"Premisa inexistente: {premise}")

        # Integridad referencial de A (constantes en Clause deben existir en O)
        for axiom in state.axioms.values():
            for clause in axiom.body:
                if not clause.source.startswith("?") and clause.source not in state.objects:
                    raise MissingReferenceError(f"Clause source inexistente en axioma '{axiom.id}': {clause.source}")
                if not clause.target.startswith("?") and clause.target not in state.objects:
                    raise MissingReferenceError(f"Clause target inexistente en axioma '{axiom.id}': {clause.target}")

        # Consistencia semántica
        self.evaluator.check_consistency(state)


# ============================================================
# KERNEL
# ============================================================

class Kernel:
    """Implementación ejecutable del núcleo MF_MIN."""

    def __init__(self, state: Optional[State] = None):
        self._state = state or State()
        self.validator = Validator()
        self.validator.validate(self._state)

    @property
    def state(self) -> State:
        return self._state

    def transition(self, transition: Transition) -> State:
        """
        δ: S x T -> S. Transición atómica con preservación del estado ante rechazo.
        
        Contrato fundamental (atomicidad por construcción):
        - Se construye un estado candidato S'
        - Se valida S' mediante Validator
        - Si V(S') = OK: el estado se reemplaza (S' ≠ S)
        - Si V(S') = FAIL: el estado anterior permanece intacto (S' = S)
        
        No existe mutación seguida de rollback. La atomicidad se logra por construcción:
        el estado anterior nunca se modifica hasta que el nuevo estado es completamente válido.
        """
        new_state = self._apply_operation(self._state, transition.operation, transition.payload)
        self.validator.validate(new_state)
        self._state = new_state
        return self._state

    def transition_batch(self, transitions: List[Transition]) -> State:
        """
        Aplica una LISTA de Transition como una única unidad atómica: se
        encadenan sobre un estado de trabajo (sin comprometer nada todavía),
        se valida el resultado FINAL una sola vez, y solo entonces se
        reemplaza self._state. Si cualquier paso falla —incluida la
        validación final— self._state queda exactamente como estaba (misma
        referencia de objeto, no una reconstrucción "equivalente": nunca se
        toca hasta el último paso, igual que en transition()).

        Por qué existe: es la generalización directa de batch_derive (que
        solo admite relaciones con origin='derived') a CUALQUIER secuencia
        de operaciones — add_object, add_relation, remove_axiom, lo que
        sea. Con esto, "componer varias propuestas en una sola decisión"
        deja de necesitar una clase Compositor nueva: basta con concatenar
        las Transition de cada propuesta, en el orden de prioridad que se
        quiera, y pasarlas aquí. Si el conjunto combinado es consistente,
        se compromete entero; si no, se rechaza entero — sin resolución de
        conflictos oculta ni heurísticas: la misma semántica de todo-o-nada
        que ya rige cada Transition individual, extendida a un lote.

        batch_derive se conserva sin cambios (compatibilidad con las 81
        pruebas existentes); transition_batch no lo reemplaza, lo generaliza.
        """
        working_state = self._state
        for t in transitions:
            working_state = self._apply_operation(working_state, t.operation, t.payload)
        self.validator.validate(working_state)
        self._state = working_state
        return self._state

    def _apply_operation(self, state: State, operation: str, payload: Mapping[str, Any]) -> State:
        """
        Construye y devuelve el estado candidato para UNA operación sobre
        UN estado dado, sin validar ni comprometer. Extraído de lo que antes
        era el cuerpo de transition() para que transition() y
        transition_batch() compartan exactamente la misma lógica por
        operación — evita que ambas rutas puedan divergir sutilmente.
        """
        if operation == "add_object":
            require_payload_fields(payload, "id", "type")
            obj = Object(
                id=payload["id"],
                type=payload["type"],
                value=payload.get("value"),
                properties=payload.get("properties", {}),
            )
            self._check_id_available(obj.id, state)

            objects = dict(state.objects)
            objects[obj.id] = obj
            return State(objects=objects, relations=state.relations, axioms=state.axioms)

        elif operation == "add_relation":
            require_payload_fields(payload, "id", "source", "predicate", "target")
            relation = Relation(
                id=payload["id"],
                source=payload["source"],
                predicate=payload["predicate"],
                target=payload["target"],
                polarity=payload.get("polarity", True),
                origin=payload.get("origin", "asserted"),
                rule_id=payload.get("rule_id"),
                premises=payload.get("premises", ()),
            )
            self._check_id_available(relation.id, state)
            self._require_objects(relation.source, relation.target, state)
            self._require_premises(relation.premises, state)

            relations = dict(state.relations)
            relations[relation.id] = relation
            return State(objects=state.objects, relations=relations, axioms=state.axioms)

        elif operation == "add_axiom":
            require_payload_fields(payload, "id", "name")
            raw_body = payload.get("body", ())
            body = tuple(
                Clause(**dict(clause)) if isinstance(clause, Mapping) else clause
                for clause in raw_body
            )
            axiom = AxiomConstraint(
                id=payload["id"],
                name=payload["name"],
                body=body,
                min_numeric_val=payload.get("min_numeric_val"),
                max_numeric_val=payload.get("max_numeric_val"),
                numeric_target_type=payload.get("numeric_target_type"),
            )
            self._check_id_available(axiom.id, state)

            axioms = dict(state.axioms)
            axioms[axiom.id] = axiom
            return State(objects=state.objects, relations=state.relations, axioms=axioms)

        elif operation == "remove_object":
            require_payload_fields(payload, "id")
            object_id = payload["id"]
            if object_id not in state.objects:
                raise MissingReferenceError(f"Objeto inexistente: {object_id}")

            dependencies = [
                relation.id for relation in state.relations.values()
                if relation.source == object_id or relation.target == object_id
            ]
            if dependencies:
                raise InvalidTransitionError(f"No se puede eliminar '{object_id}'. Dependencias: {dependencies}")

            objects = dict(state.objects)
            del objects[object_id]
            return State(objects=objects, relations=state.relations, axioms=state.axioms)

        elif operation == "remove_relation":
            require_payload_fields(payload, "id")
            relation_id = payload["id"]
            if relation_id not in state.relations:
                raise MissingReferenceError(f"Relación inexistente: {relation_id}")

            # Contrato explícito: una relación con dependientes derivados no puede eliminarse.
            self._require_relation_not_referenced(relation_id, state)

            relations = dict(state.relations)
            del relations[relation_id]
            return State(objects=state.objects, relations=relations, axioms=state.axioms)

        elif operation == "remove_axiom":
            require_payload_fields(payload, "id")
            axiom_id = payload["id"]
            if axiom_id not in state.axioms:
                raise MissingReferenceError(f"Axioma inexistente: {axiom_id}")

            axioms = dict(state.axioms)
            del axioms[axiom_id]
            return State(objects=state.objects, relations=state.relations, axioms=axioms)

        elif operation == "promote_relation":
            """
            Contrato: transforma una relación con origin='proposed' en
            origin='asserted', preservando id/source/predicate/target/
            polarity. Es la única vía formal para que un hecho propuesto
            externamente (p. ej. por un extractor basado en LLM) pase a
            contar como conocimiento aceptado del sistema — y, en
            particular, a partir de ese momento a estar disponible como
            premisa para EngineD (ver EngineD.infer_step, que excluye
            explícitamente origin='proposed' de sus índices).
            """
            require_payload_fields(payload, "id")
            rel_id = payload["id"]
            if rel_id not in state.relations:
                raise MissingReferenceError(f"Relación inexistente: {rel_id}")
            old = state.relations[rel_id]
            if old.origin != "proposed":
                raise InvalidTransitionError(
                    f"Solo se puede promover una relación con origin='proposed'; "
                    f"'{rel_id}' tiene origin='{old.origin}'."
                )
            promoted = Relation(
                id=old.id, source=old.source, predicate=old.predicate, target=old.target,
                polarity=old.polarity, origin="asserted", rule_id=None, premises=(),
            )
            relations = dict(state.relations)
            relations[rel_id] = promoted
            return State(objects=state.objects, relations=relations, axioms=state.axioms)

        elif operation == "batch_derive":
            """
            Contrato: batch_derive introduce múltiples relaciones derivadas de forma atómica.
            
            Restricciones formales:
            1. No permite dependencias internas: todas las premisas deben existir en previous.relations
            2. Rechaza cualquier origin distinto de 'derived'
            3. Las premisas no pueden referenciar relaciones dentro del mismo batch
            
            Formalmente: premises(R_i) ⊆ M(previous_state)
            NO: premises(R_i) ⊆ M(previous_state) ∪ batch
            """
            items_raw = payload.get("relations", ())

            # Validación de tipos de items
            items = []
            for i, item in enumerate(items_raw):
                if not isinstance(item, Mapping):
                    raise ValidationError(
                        f"batch_derive: item {i} debe ser Mapping."
                    )
                require_payload_fields(item, "id", "source", "predicate", "target")
                # Rechazar origin != "derived"
                item_origin = item.get("origin", "derived")
                if item_origin != "derived":
                    raise ValidationError(
                        f"batch_derive: item '{item['id']}' tiene origin='{item_origin}', "
                        f"pero batch_derive solo admite origin='derived'."
                    )
                items.append(item)

            batch_ids = [item["id"] for item in items]

            if len(batch_ids) != len(set(batch_ids)):
                raise DuplicateIDError("IDs duplicados dentro del batch.")

            for item in items:
                self._check_id_available(item["id"], state)
                self._require_objects(item["source"], item["target"], state)
                self._require_premises(item.get("premises", ()), state)

            relations = dict(state.relations)
            for item in items:
                relation = Relation(
                    id=item["id"],
                    source=item["source"],
                    predicate=item["predicate"],
                    target=item["target"],
                    polarity=item.get("polarity", True),
                    origin="derived",
                    rule_id=item.get("rule_id"),
                    premises=item.get("premises", ()),
                )
                relations[relation.id] = relation

            return State(objects=state.objects, relations=relations, axioms=state.axioms)

        else:
            raise InvalidTransitionError(f"Operación desconocida: {operation}")

    @staticmethod
    def _check_id_available(entity_id: str, state: State) -> None:
        """
        Verifica unicidad global de IDs en O, M y A.
        Nota: Rule.id pertenece al motor externo D y no está sujeto a esta restricción.
        """
        if entity_id in state.objects or entity_id in state.relations or entity_id in state.axioms:
            raise DuplicateIDError(f"ID global ocupado: '{entity_id}'")

    @staticmethod
    def _require_objects(source: str, target: str, state: State) -> None:
        if source not in state.objects:
            raise MissingReferenceError(f"Objeto origen inexistente: {source}")
        if target not in state.objects:
            raise MissingReferenceError(f"Objeto destino inexistente: {target}")

    @staticmethod
    def _require_premises(premises: Tuple[str, ...], state: State) -> None:
        for premise in premises:
            if premise not in state.relations:
                raise MissingReferenceError(f"Premisa inexistente: {premise}")

    @staticmethod
    def _require_relation_not_referenced(relation_id: str, state: State) -> None:
        """
        Contrato explícito de δ: una relación que es premisa de otra relación
        derivada no puede eliminarse.
        """
        dependents = [
            relation.id
            for relation in state.relations.values()
            if relation_id in relation.premises
        ]
        if dependents:
            raise InvalidTransitionError(
                f"No se puede eliminar '{relation_id}'. Es premisa de: {dependents}"
            )



# ============================================================
# NOTA ARQUITECTÓNICA: CAPA 2 (MOTOR D) DESACOPLADA
# ============================================================
# EngineD, Rule y Pattern han sido trasladados a 'engine_d.py'.
# La dependencia es estrictamente:
#     engine_d -> mf_min_definitivo
# El núcleo formal MF_MIN = ⟨O, M, A, δ⟩ permanece puro y cerrado.
# ============================================================

# ============================================================
# π — PROYECCIÓN SEMÁNTICA RELACIONAL
# ============================================================

def project_pi(state: State) -> Set[Tuple[str, str, str, bool]]:
    """
    π_M: Proyección semántica de la estructura relacional pura.
    Extrae M_sem eliminando IDs operacionales, procedencia y metadatos.
    
    Nota importante: π_M es una proyección parcial, NO una equivalencia completa de estados.
    π_M(S1) = π_M(S2) NO implica que S1 y S2 sean equivalentes en O ni en A.
    Solo garantiza equivalencia en la estructura relacional pura.
    
    Propiedades:
    - Determinismo: π_M(S) produce el mismo resultado para el mismo estado
    - Estabilidad: π_M(S) no depende del orden de inserción de relaciones
    - Invariancia: π_M elimina metadatos operacionales (id, origin, rule_id, premises)
    """
    return {
        (relation.source, relation.predicate, relation.target, relation.polarity)
        for relation in state.relations.values()
    }


def states_equivalent(s1: State, s2: State) -> bool:
    """
    Relación de equivalencia semántica  S1 ~π S2  ⟺  π_M(S1) = π_M(S2).

    Reincorporada tras pruebas cruzadas: se formaliza como función explícita
    y nombrada (antes solo existían comparaciones ad hoc `pi_1 == pi_2`
    dentro de tests sueltos, sin una función que representara la relación
    en sí). En GRUPO E se demuestra con casos construidos que es reflexiva,
    simétrica y transitiva, y que además discrimina correctamente estados
    con contenido distinto (no es trivialmente verdadera).
    """
    return project_pi(s1) == project_pi(s2)


# ============================================================
# CAPA 4 — PERSISTENCIA
# ============================================================
# Antes, MF_MIN solo existía en memoria: cerrar el proceso significaba
# perder el estado. Estas funciones serializan/deserializan State a JSON.
#
# Limitación conocida y deliberadamente no ocultada: JSON no distingue
# tuple/list ni set/frozenset/list, y exige claves de objeto en string. Por
# tanto, un valor `frozenset` en Object.value/properties, o una clave de
# dict que no sea string, sobreviven un ciclo guardar→cargar con un tipo
# distinto (típicamente lista, y clave convertida a string) aunque su
# CONTENIDO se preserve. Para los tipos que freeze_value() trata como
# canónicos en la práctica de este núcleo (dict/list/tuple + escalares),
# el ciclo es exacto.

def _to_plain(value: Any) -> Any:
    """Convierte estructuras congeladas de MF_MIN a tipos planos serializables en JSON."""
    if isinstance(value, Mapping):
        return {str(k): _to_plain(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_to_plain(v) for v in value]
    if isinstance(value, (set, frozenset)):
        return [_to_plain(v) for v in value]
    return value


def state_to_dict(state: State) -> Dict[str, Any]:
    """Convierte un State inmutable en un dict de tipos planos, listo para json.dumps()."""
    return {
        "objects": {
            oid: {"id": o.id, "type": o.type, "value": _to_plain(o.value), "properties": _to_plain(o.properties)}
            for oid, o in state.objects.items()
        },
        "relations": {
            rid: {
                "id": r.id, "source": r.source, "predicate": r.predicate, "target": r.target,
                "polarity": r.polarity, "origin": r.origin, "rule_id": r.rule_id,
                "premises": list(r.premises),
            }
            for rid, r in state.relations.items()
        },
        "axioms": {
            aid: {
                "id": a.id, "name": a.name,
                "body": [
                    {"predicate": c.predicate, "source": c.source, "target": c.target, "polarity": c.polarity}
                    for c in a.body
                ],
                "min_numeric_val": a.min_numeric_val,
                "max_numeric_val": a.max_numeric_val,
                "numeric_target_type": a.numeric_target_type,
            }
            for aid, a in state.axioms.items()
        },
    }


def state_from_dict(data: Mapping[str, Any]) -> State:
    """Reconstruye un State a partir del dict producido por state_to_dict()."""
    objects = {
        oid: Object(id=o["id"], type=o["type"], value=o.get("value"), properties=o.get("properties", {}))
        for oid, o in data.get("objects", {}).items()
    }
    relations = {
        rid: Relation(
            id=r["id"], source=r["source"], predicate=r["predicate"], target=r["target"],
            polarity=r.get("polarity", True), origin=r.get("origin", "asserted"),
            rule_id=r.get("rule_id"), premises=tuple(r.get("premises", ())),
        )
        for rid, r in data.get("relations", {}).items()
    }
    axioms = {
        aid: AxiomConstraint(
            id=a["id"], name=a["name"],
            body=tuple(Clause(**c) for c in a.get("body", ())),
            min_numeric_val=a.get("min_numeric_val"),
            max_numeric_val=a.get("max_numeric_val"),
            numeric_target_type=a.get("numeric_target_type"),
        )
        for aid, a in data.get("axioms", {}).items()
    }
    return State(objects=objects, relations=relations, axioms=axioms)


def save_state(state: State, path: str) -> None:
    """Guarda un State como JSON en disco. No valida — usar Kernel(load_state(path)) para eso."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(state_to_dict(state), f, ensure_ascii=False, indent=2)


def load_state(path: str) -> State:
    """Carga un State desde un archivo JSON producido por save_state()."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return state_from_dict(data)



# (La persistencia de reglas save_rules/load_rules reside en engine_d.py)


# ============================================================
# CAPA 5 — RENDIMIENTO
# ============================================================
# _RelationIndex (usada por EngineD) y _PredicatePolarityIndex (usada por
# EvaluatorA, definida junto a esa clase en CAPA 1) existen porque, medido
# — no supuesto — dos caminos escalaban mal:
#   (a) EvaluatorA volvía a escanear TODAS las relaciones por cada cláusula
#       de cada axioma, en CADA transición (no solo durante derivación).
#       Corregido: índice (predicate, polarity) compartido por verificación.
#   (b) EngineD.infer_step comprobaba "¿esta conclusión ya existe?" con un
#       escaneo lineal POR CANDIDATO derivado. Corregido: un solo
#       project_pi() por llamada, membresía O(1) después.
#
# Límite honesto que NINGUNO de los dos arreglos elimina: una regla de 2+
# premisas que computa clausura transitiva sobre una relación que crece a
# O(n²) genera, por evaluación ingenua (re-unir TODO contra TODO en cada
# ronda, no solo lo nuevo contra lo visto), del orden de O(n³) pares
# candidato en total. Medido: n=45 nodos en cadena → 0.14s; n=200 → 14.5s.
# Los índices reducen CUÁNTO cuesta examinar cada candidato; no reducen
# CUÁNTOS candidatos hay que examinar cuando el problema es
# combinatoriamente así de grande. La solución real a esto es "evaluación
# semi-ingenua" (unir solo lo derivado en la ronda anterior contra el resto,
# no todo contra todo) — un cambio algorítmico más profundo, no una
# optimización de índice, y queda fuera de esta sesión. Lo que SÍ se
# entrega en su lugar: max_rounds/max_total_derived en saturate() para que
# ese costo, cuando ocurra, aborte con un error accionable en vez de
# consumir tiempo/memoria sin aviso.


# ============================================================
# CAPA 6 — CONCURRENCIA
# ============================================================

class ThreadSafeKernel:
    """
    Envoltura de Kernel que serializa las llamadas a transition() con un
    RLock, para uso concurrente seguro desde múltiples hilos.

    Motivo (el problema es real, no hipotético): Kernel.transition() lee
    self._state, construye un estado candidato a partir de esa lectura, y
    solo al final reasigna self._state. Sin sincronización, dos hilos
    pueden leer el MISMO estado previo, construir cada uno su candidato de
    forma independiente, y el que reasigna self._state en segundo lugar
    sobrescribe silenciosamente el cambio del primero ("lost update") —
    sin ninguna excepción que lo delate.

    Esta envoltura da exclusión mutua (nunca dos transiciones se procesan
    en paralelo), NO paralelismo real de escritura ni lectura sin bloqueo.
    Para el patrón de uso actual de MF_MIN (invocación desde procesos con
    ráfagas de transiciones, no escritura sostenida de alta frecuencia
    entre muchos hilos), esta granularidad basta y evita la complejidad
    adicional — y el riesgo de introducir errores nuevos — de un diseño
    lock-free.
    """

    def __init__(self, state: Optional[State] = None):
        self._kernel = Kernel(state)
        self._lock = threading.RLock()

    @property
    def state(self) -> State:
        with self._lock:
            return self._kernel.state

    @property
    def validator(self) -> Validator:
        return self._kernel.validator

    def transition(self, t: Transition) -> State:
        with self._lock:
            return self._kernel.transition(t)

    def transition_batch(self, transitions: List[Transition]) -> State:
        with self._lock:
            return self._kernel.transition_batch(transitions)


# ============================================================
# CAPA 6.5 — PROPONENTES (propuesta ≠ autoridad)
# ============================================================
# Un proponente es, por convención, CUALQUIER función que reciba algo y
# devuelva List[Transition] SIN aplicarlas. No requiere clase base, no
# requiere una representación intermedia nueva (Transition ya es la IR: es
# serializable, ya pasa por freeze_value, ya la consume Kernel). Quien llama
# decide si aplica la propuesta (vía kernel.transition_batch(...), que la
# compromete entera o la rechaza entera) y con qué origin.
#
# extract_facts_from_text() es el primer proponente real, no especulativo:
# toma texto y devuelve relaciones candidatas con origin="proposed" — NO
# "asserted" ni "derived". Eso es deliberado: una propuesta externa entra
# marcada como no verificada, no puede alimentar EngineD hasta que se
# promueva explícitamente (Transition("promote_relation", {"id": ...})), y
# mientras tanto sigue sujeta a I1-I6 igual que cualquier otro hecho (un
# axioma puede rechazarla si es inconsistente con lo ya sabido).
#
# El parser de abajo es un SUSTITUTO explícito de una llamada real a un LLM.
# Este entorno no tiene acceso de red a APIs de modelos (solo a registros de
# paquetes), así que no se puede invocar un LLM de verdad aquí sin fingirlo.
# Lo que SÍ es real y probado es el contrato: texto -> List[Transition] con
# origin="proposed", listas para pasar por kernel.transition_batch(). Sustituir
# _parse_simple_implications() por una llamada al API de un modelo (pidiendo
# JSON con ese mismo formato de salida) es un cambio de una función, no un
# rediseño.

_IMPLICATION_PATTERN = re.compile(
    r"([A-Za-zÀ-ÿ0-9_ ]+?)\s*(?:->|→|implica|se relaciona con|relacionado con)\s*([A-Za-zÀ-ÿ0-9_ ]+)",
    re.IGNORECASE,
)


def _slugify(label: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9_]+", "_", label.strip().lower()).strip("_")
    return slug or "entidad"


def _parse_simple_implications(text: str) -> List[Tuple[str, str]]:
    """
    Sustituto determinista de una llamada a LLM: reconoce oraciones del tipo
    'A -> B', 'A implica B', 'A relacionado con B' (una por línea o separadas
    por coma/punto), y devuelve pares (fuente, destino) en su forma legible
    original. No pretende ser un parser de lenguaje natural general — solo
    demuestra el contrato de entrada/salida que un extractor real (basado en
    LLM) debería cumplir.
    """
    pairs: List[Tuple[str, str]] = []
    for chunk in re.split(r"[\n\.;]+", text):
        chunk = chunk.strip()
        if not chunk:
            continue
        m = _IMPLICATION_PATTERN.search(chunk)
        if m:
            pairs.append((m.group(1).strip(), m.group(2).strip()))
    return pairs


def extract_facts_from_text(
    text: str,
    kernel: Kernel,
    predicate: str = "implica",
    object_type: str = "Entidad",
    id_prefix: str = "prop",
) -> List[Transition]:
    """
    Proponente de ejemplo: texto -> List[Transition], SIN aplicarlas.

    Para cada entidad mencionada que no exista ya en `kernel.state.objects`,
    propone un add_object; para cada par reconocido, propone un add_relation
    con origin="proposed". El llamador decide si compromete la propuesta —
    típicamente con kernel.transition_batch(propuestas) — y más tarde, si la
    confirma por otra vía, con Transition("promote_relation", {"id": ...}).

    No consulta ni modifica el Kernel: solo LEE su estado actual para saber
    qué entidades ya existen y así no proponer duplicados innecesarios.
    """
    pairs = _parse_simple_implications(text)
    proposals: List[Transition] = []
    seen_object_ids: Set[str] = set(kernel.state.objects.keys())
    counter = 0

    def _ensure_object(label: str) -> str:
        nonlocal counter
        obj_id = _slugify(label)
        if obj_id not in seen_object_ids:
            proposals.append(Transition("add_object", {"id": obj_id, "type": object_type, "value": label}))
            seen_object_ids.add(obj_id)
        return obj_id

    for source_label, target_label in pairs:
        source_id = _ensure_object(source_label)
        target_id = _ensure_object(target_label)
        counter += 1
        rel_id = f"{id_prefix}_{counter}_{source_id}_{target_id}"
        proposals.append(Transition("add_relation", {
            "id": rel_id, "source": source_id, "predicate": predicate, "target": target_id,
            "polarity": True, "origin": "proposed",
        }))

    return proposals


# ============================================================

# ============================================================
# NOTA ARQUITECTÓNICA: CAPA DE USO (MFMin) DESACOPLADA
# ============================================================
# La fachada ergonómica MFMin ha sido trasladada a 'mf_min_facade.py'.
# ============================================================

# ============================================================
# CAPA 3: BATERÍA DE CIERRE MF_MIN v1.0.2
# ============================================================

def run_mf_min_closure_suite() -> Tuple[List[Tuple[str, bool, str]], bool]:
    # Importaciones de componentes desacoplados para la batería de cierre
    from engine_d import EngineD, Rule, Pattern, save_rules, load_rules
    from mf_min_facade import MFMin
    suite_results: List[Tuple[str, bool, str]] = []

    # ------------------------------------------------------------
    # GRUPO A: INTEGRIDAD ESTRUCTURAL
    # ------------------------------------------------------------

    # A1: Inmutabilidad y Tipado Seguro
    k_a1 = Kernel()
    try:
        class CustomObj: pass
        k_a1.transition(Transition("add_object", {"id": "bad_obj", "type": "Test", "value": CustomObj()}))
        a1_ok = False
    except TypeError:
        k_a1.transition(Transition("add_object", {"id": "good_obj", "type": "Test", "properties": {"nested": [1, 2]}}))
        a1_ok = ("good_obj" in k_a1.state.objects)
    suite_results.append(("A1. Inmutabilidad y Tipado Seguro", a1_ok, "Solo tipos congelables; mutaciones externas no afectan."))

    # A2: IDs Globalmente Únicos
    k_a2 = Kernel()
    k_a2.transition(Transition("add_object", {"id": "n1", "type": "N"}))
    try:
        k_a2.transition(Transition("add_object", {"id": "n1", "type": "N"}))
        a2_ok = False
    except DuplicateIDError:
        a2_ok = True
    suite_results.append(("A2. Unicidad Global de IDs", a2_ok, "El Kernel rechaza IDs duplicados en O, M, A."))

    # A3: Identidad Key == ID
    k_a3 = Kernel()
    k_a3.transition(Transition("add_object", {"id": "obj1", "type": "T"}))
    a3_ok = (k_a3.state.objects["obj1"].id == "obj1")
    suite_results.append(("A3. Identidad Key == ID", a3_ok, "La clave del mapping coincide con el ID interno."))

    # A4: Integridad Referencial Estricta
    k_a4 = Kernel()
    k_a4.transition(Transition("add_object", {"id": "n1", "type": "N"}))
    try:
        k_a4.transition(Transition("add_relation", {"id": "r_bad", "source": "n1", "predicate": "link", "target": "non_existent"}))
        a4_ok = False
    except MissingReferenceError:
        a4_ok = (len(k_a4.state.relations) == 0)
    suite_results.append(("A4. Integridad Referencial Estricta", a4_ok, "Imposible crear relaciones a objetos inexistentes."))

    # A5: Tipos Numéricos
    k_a5 = Kernel()
    k_a5.transition(Transition("add_axiom", {"id": "AX_NUM", "name": "NumBound", "numeric_target_type": "Metric", "min_numeric_val": 0.0, "max_numeric_val": 100.0}))
    errors = 0
    for val in [True, float('nan'), float('inf'), -1, 101]:
        try:
            k_a5.transition(Transition("add_object", {"id": f"m_{val}", "type": "Metric", "value": val}))
        except ContradictionError:
            errors += 1
    k_a5.transition(Transition("add_object", {"id": "m_ok", "type": "Metric", "value": 50.0}))
    a5_ok = (errors == 5 and "m_ok" in k_a5.state.objects)
    suite_results.append(("A5. Control Numérico Estricto", a5_ok, "Rechazo de Bool, NaN, Inf y fuera de rango."))

    # A6: Límites numéricos NaN/Inf rechazados en axioma
    a6_nan_ok = False
    a6_inf_ok = False

    try:
        AxiomConstraint(id="AX_BAD", name="Bad", min_numeric_val=float("nan"))
    except ValidationError:
        a6_nan_ok = True

    try:
        AxiomConstraint(id="AX_BAD2", name="Bad2", max_numeric_val=float("inf"))
    except ValidationError:
        a6_inf_ok = True

    a6_ok = a6_nan_ok and a6_inf_ok
    suite_results.append(("A6. Límites Numéricos Finitos", a6_ok, "AxiomConstraint rechaza NaN/Inf como límites."))

    # A7: Unicidad semántica de hechos (I4) — reincorporada tras pruebas cruzadas
    k_a7 = Kernel()
    k_a7.transition(Transition("add_object", {"id": "p7", "type": "N"}))
    k_a7.transition(Transition("add_object", {"id": "q7", "type": "N"}))
    k_a7.transition(Transition("add_relation", {"id": "F1_A7", "source": "p7", "predicate": "vinculo", "target": "q7", "polarity": True}))
    s_before_a7 = k_a7.state
    a7_ok = False
    try:
        k_a7.transition(Transition("add_relation", {"id": "F2_A7", "source": "p7", "predicate": "vinculo", "target": "q7", "polarity": True}))
    except DuplicateFactError:
        a7_ok = (k_a7.state == s_before_a7) and (len(k_a7.state.relations) == 1)
    suite_results.append((
        "A7. Unicidad Semántica de Hechos (I4)", a7_ok,
        "Dos identificadores distintos no pueden afirmar el mismo triple (source,predicate,target) en la misma polaridad."
    ))

    # ------------------------------------------------------------
    # GRUPO B: SEMÁNTICA
    # ------------------------------------------------------------

    # B1-B3: TRUE, FALSE, UNKNOWN
    k_b = Kernel()
    k_b.transition(Transition("add_object", {"id": "u1", "type": "U"}))
    k_b.transition(Transition("add_object", {"id": "r1", "type": "R"}))
    k_b.transition(Transition("add_relation", {"id": "POS", "source": "u1", "predicate": "acc", "target": "r1", "polarity": True}))
    k_b.transition(Transition("add_relation", {"id": "NEG", "source": "u1", "predicate": "deny", "target": "r1", "polarity": False}))
    
    d_b = EngineD(k_b)
    b1_ok = (d_b.query_evidence("u1", "acc", "r1") == "TRUE")
    b2_ok = (d_b.query_evidence("u1", "deny", "r1") == "FALSE")
    b3_ok = (d_b.query_evidence("u1", "acc", "r_nonexistent") == "UNKNOWN")
    suite_results.append(("B1. Evidencia TRUE", b1_ok, "Consulta positiva correcta."))
    suite_results.append(("B2. Evidencia FALSE", b2_ok, "Consulta negativa correcta."))
    suite_results.append(("B3. Evidencia UNKNOWN", b3_ok, "Ausencia de información correcta."))

    # B4: Contradicción Directa
    contra_blocked = False
    try:
        k_b.transition(Transition("add_relation", {"id": "BAD", "source": "u1", "predicate": "acc", "target": "r1", "polarity": False}))
    except ContradictionError:
        contra_blocked = True
    suite_results.append(("B4. Veto de Contradicción Directa", contra_blocked, "Kernel impide P y ¬P simultáneos."))

    # B5: __distinct__ Correcto
    k_b5 = Kernel()
    k_b5.transition(Transition("add_object", {"id": "x1", "type": "E"}))
    k_b5.transition(Transition("add_object", {"id": "x2", "type": "E"}))
    k_b5.transition(Transition("add_axiom", {
        "id": "AX_DIST", "name": "OnlySelfLoop",
        "body": (
            {"predicate": "conn", "source": "?X", "target": "?Y", "polarity": True},
            {"predicate": "__distinct__", "source": "?X", "target": "?Y", "polarity": True}
        )
    }))
    
    k_b5.transition(Transition("add_relation", {"id": "R_REFL", "source": "x1", "predicate": "conn", "target": "x1"}))
    
    distinct_triggered = False
    try:
        k_b5.transition(Transition("add_relation", {"id": "R_DIFF", "source": "x1", "predicate": "conn", "target": "x2"}))
    except ContradictionError:
        distinct_triggered = True
        
    b5_ok = ("R_REFL" in k_b5.state.relations) and distinct_triggered
    suite_results.append(("B5. Semántica __distinct__", b5_ok, "Axioma prohíbe conn(X,Y) cuando X ≠ Y (solo self-loops)."))

    # B6: Unificación Conjuntiva
    k_b6 = Kernel()
    for o in ["a", "b", "c"]: k_b6.transition(Transition("add_object", {"id": o, "type": "N"}))
    k_b6.transition(Transition("add_relation", {"id": "R_AB", "source": "a", "predicate": "step", "target": "b"}))
    k_b6.transition(Transition("add_relation", {"id": "R_BC", "source": "b", "predicate": "step", "target": "c"}))
    k_b6.transition(Transition("add_relation", {"id": "R_AC", "source": "a", "predicate": "step", "target": "c"}))
    
    try:
        k_b6.transition(Transition("add_axiom", {
            "id": "AX_REDUNDANT", "name": "NoRedundantTrans",
            "body": (
                {"predicate": "step", "source": "?A", "target": "?B", "polarity": True},
                {"predicate": "step", "source": "?B", "target": "?C", "polarity": True},
                {"predicate": "step", "source": "?A", "target": "?C", "polarity": True}
            )
        }))
        b6_ok = False
    except ContradictionError:
        b6_ok = True
        
    suite_results.append(("B6. Unificación Conjuntiva", b6_ok, "Axioma detecta patrón complejo con variables compartidas."))

    # B7: Validación de Clause
    try:
        Clause("", "?X", "?Y")
        b7_ok = False
    except ValidationError:
        b7_ok = True
    suite_results.append(("B7. Validación de Clause", b7_ok, "Clause rechaza predicate/source/target vacíos."))

    # B8: __distinct__ Independiente del Orden
    k_b8a = Kernel()
    k_b8a.transition(Transition("add_object", {"id": "x1", "type": "E"}))
    k_b8a.transition(Transition("add_object", {"id": "x2", "type": "E"}))
    k_b8a.transition(Transition("add_axiom", {
        "id": "AX_DIST_ORDER_A", "name": "DistinctFirst",
        "body": (
            {"predicate": "__distinct__", "source": "?X", "target": "?Y", "polarity": True},
            {"predicate": "conn", "source": "?X", "target": "?Y", "polarity": True}
        )
    }))
    distinct_triggered_a = False
    try:
        k_b8a.transition(Transition("add_relation", {"id": "R_CONN_12_A", "source": "x1", "predicate": "conn", "target": "x2"}))
    except ContradictionError:
        distinct_triggered_a = True

    k_b8b = Kernel()
    k_b8b.transition(Transition("add_object", {"id": "x1", "type": "E"}))
    k_b8b.transition(Transition("add_object", {"id": "x2", "type": "E"}))
    k_b8b.transition(Transition("add_axiom", {
        "id": "AX_DIST_ORDER_B", "name": "ConnFirst",
        "body": (
            {"predicate": "conn", "source": "?X", "target": "?Y", "polarity": True},
            {"predicate": "__distinct__", "source": "?X", "target": "?Y", "polarity": True}
        )
    }))
    distinct_triggered_b = False
    try:
        k_b8b.transition(Transition("add_relation", {"id": "R_CONN_12_B", "source": "x1", "predicate": "conn", "target": "x2"}))
    except ContradictionError:
        distinct_triggered_b = True

    b8_ok = distinct_triggered_a and distinct_triggered_b
    suite_results.append(("B8. __distinct__ Independiente del Orden", b8_ok, "El orden textual de las cláusulas no altera la semántica."))

    # B9: Integridad referencial de constantes en Clause
    k_b9 = Kernel()
    k_b9.transition(Transition("add_object", {"id": "x1", "type": "E"}))
    try:
        k_b9.transition(Transition("add_axiom", {
            "id": "AX_GHOST", "name": "GhostRef",
            "body": ({"predicate": "p", "source": "ghost", "target": "x1", "polarity": True},)
        }))
        b9_ok = False
    except MissingReferenceError:
        b9_ok = True
    suite_results.append(("B9. Integridad Referencial en Clause", b9_ok, "Constantes en Clause deben existir en O."))

    # ------------------------------------------------------------
    # GRUPO C: δ (TRANSICIONES)
    # ------------------------------------------------------------

    # C1: Ciclo de Vida Básico
    k_c = Kernel()
    k_c.transition(Transition("add_object", {"id": "o1", "type": "T"}))
    k_c.transition(Transition("add_relation", {"id": "r1", "source": "o1", "predicate": "p", "target": "o1"}))
    k_c.transition(Transition("remove_relation", {"id": "r1"}))
    k_c.transition(Transition("remove_object", {"id": "o1"}))
    c1_ok = (len(k_c.state.objects) == 0)
    suite_results.append(("C1. Ciclo de Vida Básico", c1_ok, "Add y Remove funcionan correctamente."))

    # C3: Rechazo de Transición Inválida
    k_c.transition(Transition("add_object", {"id": "persistent", "type": "T"}))
    try:
        k_c.transition(Transition("add_object", {"id": "persistent", "type": "T"}))
        c3_ok = False
    except DuplicateIDError:
        c3_ok = True
    suite_results.append(("C3. Rechazo de Transición Inválida", c3_ok, "ID duplicado rechazado."))

    # C4: Atomicidad por Construcción
    s_pre = k_c.state
    try:
        k_c.transition(Transition("add_relation", {"id": "r_bad", "source": "persistent", "predicate": "p", "target": "non_existent"}))
    except KernelError:
        pass
    c4_ok = (k_c.state == s_pre)
    suite_results.append(("C4. Atomicidad por Construcción", c4_ok, "Estado anterior preservado ante transición rechazada."))

    # C5: Atomicidad de Batch
    k_c5 = Kernel()
    k_c5.transition(Transition("add_object", {"id": "n1", "type": "N"}))
    k_c5.transition(Transition("add_object", {"id": "n2", "type": "N"}))
    
    batch_invalid = [
        {"id": "R_GOOD", "source": "n1", "predicate": "link", "target": "n2"},
        {"id": "R_BAD", "source": "n1", "predicate": "link", "target": "non_existent"}
    ]
    
    try:
        k_c5.transition(Transition("batch_derive", {"relations": batch_invalid}))
        c5_ok = False
    except MissingReferenceError:
        c5_ok = (len(k_c5.state.relations) == 0)
    suite_results.append(("C5. Atomicidad de Batch", c5_ok, "Batch rechazado no deja residuos."))

    # C6: Eliminación de Axioma
    k_c6 = Kernel()
    k_c6.transition(Transition("add_object", {"id": "x", "type": "X"}))
    k_c6.transition(Transition("add_axiom", {"id": "AX1", "name": "Test"}))
    k_c6.transition(Transition("remove_axiom", {"id": "AX1"}))
    c6_ok = "AX1" not in k_c6.state.axioms
    suite_results.append(("C6. Eliminación de Axioma", c6_ok, "remove_axiom elimina realmente el axioma del estado."))

    # C7: Integridad de Premisas
    k_c7 = Kernel()
    k_c7.transition(Transition("add_object", {"id": "n1", "type": "N"}))
    try:
        k_c7.transition(Transition("add_relation", {
            "id": "r_bad_prem", "source": "n1", "predicate": "p", "target": "n1",
            "premises": ("non_existent_premise",)
        }))
        c7_ok = False
    except MissingReferenceError:
        c7_ok = True
    suite_results.append(("C7. Integridad de Premisas", c7_ok, "Relación con premisa inexistente es rechazada."))

    # C8: Eliminación de relación con dependientes derivados
    k_c8 = Kernel()
    k_c8.transition(Transition("add_object", {"id": "a", "type": "N"}))
    k_c8.transition(Transition("add_object", {"id": "b", "type": "N"}))
    k_c8.transition(Transition("add_object", {"id": "c", "type": "N"}))
    k_c8.transition(Transition("add_relation", {"id": "R_AB", "source": "a", "predicate": "step", "target": "b"}))
    k_c8.transition(Transition("add_relation", {"id": "R_BC", "source": "b", "predicate": "step", "target": "c"}))
    k_c8.transition(Transition("add_relation", {
        "id": "R_AC", "source": "a", "predicate": "step", "target": "c",
        "origin": "derived", "rule_id": "R_TRANS", "premises": ("R_AB", "R_BC")
    }))
    
    try:
        k_c8.transition(Transition("remove_relation", {"id": "R_AB"}))
        c8_ok = False
    except InvalidTransitionError:
        c8_ok = True
    suite_results.append(("C8. Eliminación de Relación con Dependientes", c8_ok, "No se puede eliminar una relación que es premisa de otra."))

    # C9: batch_derive sin dependencias internas
    k_c9 = Kernel()
    k_c9.transition(Transition("add_object", {"id": "n1", "type": "N"}))
    k_c9.transition(Transition("add_object", {"id": "n2", "type": "N"}))
    k_c9.transition(Transition("add_object", {"id": "n3", "type": "N"}))
    
    batch_internal_dep = [
        {"id": "R1", "source": "n1", "predicate": "link", "target": "n2", "origin": "derived", "rule_id": "R", "premises": ()},
        {"id": "R2", "source": "n2", "predicate": "link", "target": "n3", "origin": "derived", "rule_id": "R", "premises": ("R1",)}
    ]
    
    try:
        k_c9.transition(Transition("batch_derive", {"relations": batch_internal_dep}))
        c9_ok = False
    except MissingReferenceError:
        c9_ok = True
    suite_results.append(("C9. Batch sin Dependencias Internas", c9_ok, "batch_derive no permite premisas dentro del mismo batch."))

    # C10: Payload incompleto lanza ValidationError
    k_c10 = Kernel()
    try:
        k_c10.transition(Transition("add_object", {"type": "N"}))  # falta id
        c10_ok = False
    except ValidationError:
        c10_ok = True
    suite_results.append(("C10. Payload Incompleto", c10_ok, "Payload sin campos obligatorios lanza ValidationError."))

    # C11: batch_derive con item no-Mapping
    k_c11 = Kernel()
    k_c11.transition(Transition("add_object", {"id": "n1", "type": "N"}))
    try:
        k_c11.transition(Transition("batch_derive", {"relations": ("not_a_mapping",)}))
        c11_ok = False
    except ValidationError:
        c11_ok = True
    suite_results.append(("C11. Batch con Item No-Mapping", c11_ok, "batch_derive rechaza items que no son Mapping."))

    # C12: batch_derive con origin != "derived"
    k_c12 = Kernel()
    k_c12.transition(Transition("add_object", {"id": "n1", "type": "N"}))
    k_c12.transition(Transition("add_object", {"id": "n2", "type": "N"}))
    try:
        k_c12.transition(Transition("batch_derive", {"relations": [
            {"id": "R_BAD", "source": "n1", "predicate": "p", "target": "n2", "origin": "asserted"}
        ]}))
        c12_ok = False
    except ValidationError:
        c12_ok = True
    suite_results.append(("C12. Batch Rechaza origin != derived", c12_ok, "batch_derive rechaza origin='asserted'."))

    # C13: Invariante de Estado tras toda transición aceptada
    k_c13 = Kernel()
    k_c13.transition(Transition("add_object", {"id": "x", "type": "X"}))
    k_c13.transition(Transition("add_object", {"id": "y", "type": "Y"}))
    k_c13.transition(Transition("add_relation", {"id": "r1", "source": "x", "predicate": "p", "target": "y"}))
    
    # Verificar que el estado es válido después de cada transición
    c13_ok = True
    try:
        k_c13.validator.validate(k_c13.state)
    except Exception:
        c13_ok = False
    
    # Verificar que transiciones inválidas no alteran el estado
    s_before = k_c13.state
    try:
        k_c13.transition(Transition("add_relation", {"id": "r_bad", "source": "x", "predicate": "p", "target": "nonexistent"}))
    except MissingReferenceError:
        pass
    c13_ok = c13_ok and (k_c13.state == s_before)
    
    suite_results.append(("C13. Invariante de Estado", c13_ok, "Toda transición aceptada produce estado válido; rechazada conserva estado."))

    # C14: Aislamiento del estado anterior
    k_c14 = Kernel()
    k_c14.transition(Transition("add_object", {"id": "obj1", "type": "T"}))
    s1 = k_c14.state
    k_c14.transition(Transition("add_object", {"id": "obj2", "type": "T"}))
    s2 = k_c14.state
    
    c14_ok = (s1 is not s2) and (s1 != s2) and ("obj1" in s1.objects) and ("obj2" not in s1.objects)
    suite_results.append(("C14. Aislamiento de Estado Anterior", c14_ok, "Estado anterior permanece intacto e inalterado."))

    # ------------------------------------------------------------
    # GRUPO D: MOTOR D
    # ------------------------------------------------------------

    # D1: Inferencia Básica
    k_d = Kernel()
    for o in ["a", "b", "c"]: k_d.transition(Transition("add_object", {"id": o, "type": "N"}))
    k_d.transition(Transition("add_relation", {"id": "R_AB", "source": "a", "predicate": "step", "target": "b"}))
    k_d.transition(Transition("add_relation", {"id": "R_BC", "source": "b", "predicate": "step", "target": "c"}))
    
    engine = EngineD(k_d)
    rule_trans = Rule("R_TRANS", "Transitivity",
                      (Pattern("step", "?A", "?B"), Pattern("step", "?B", "?C")),
                      Pattern("step", "?A", "?C"))
    
    count = engine.saturate([rule_trans])
    derived_rels = [r for r in k_d.state.relations.values() if r.origin == "derived"]
    d1_ok = (count == 1 and len(derived_rels) == 1)
    suite_results.append(("D1. Inferencia Básica", d1_ok, "Motor D deriva consecuencias correctas."))

    # D2: Variables Compartidas
    d2_ok = (derived_rels[0].source == "a" and derived_rels[0].target == "c")
    suite_results.append(("D2. Unificación de Variables Compartidas", d2_ok, "Variable intermedia ?B se une correctamente."))

    # D3: Procedencia
    d3_ok = (derived_rels[0].rule_id == "R_TRANS" and len(derived_rels[0].premises) == 2)
    suite_results.append(("D3. Procedencia Trazable", d3_ok, "Derivaciones conservan regla y premisas."))

    # D4: IDs Deterministas de Derivación
    d4_ok = derived_rels[0].id.startswith("D_")
    suite_results.append(("D4. IDs Deterministas de Derivación", d4_ok, "IDs reproducibles para misma regla y conclusión."))

    # D5: Saturación y Terminación
    k_d5 = Kernel()
    for o in ["a", "b", "c", "d"]: k_d5.transition(Transition("add_object", {"id": o, "type": "N"}))
    k_d5.transition(Transition("add_relation", {"id": "R_AB", "source": "a", "predicate": "step", "target": "b"}))
    k_d5.transition(Transition("add_relation", {"id": "R_BC", "source": "b", "predicate": "step", "target": "c"}))
    k_d5.transition(Transition("add_relation", {"id": "R_CD", "source": "c", "predicate": "step", "target": "d"}))
    
    engine5 = EngineD(k_d5)
    count5 = engine5.saturate([rule_trans])
    d5_ok = (count5 == 3)
    suite_results.append(("D5. Saturación y Terminación", d5_ok, "Saturación completa en cadena."))

    # D6: Regla Mal Formada
    try:
        bad_rule = Rule("R_BAD", "Bad",
                        (Pattern("step", "?A", "?B"),),
                        Pattern("step", "?A", "?FREE"))
        d6_ok = False
    except ValidationError:
        d6_ok = True
    suite_results.append(("D6. Rechazo de Reglas Mal Formadas", d6_ok, "Variables de conclusión no ligadas son rechazadas."))

    # D7: Rule con premisa vacía
    try:
        Rule("R_BAD_PREM", "Bad Premise", (Pattern("", "?A", "?B"),), Pattern("step", "?A", "?B"))
        d7_ok = False
    except ValidationError:
        d7_ok = True
    suite_results.append(("D7. Rechazo de Premisa Vacía en Rule", d7_ok, "Rule rechaza premisas con predicate/source/target vacíos."))

    # D8: Rule con conclusión source/target vacío
    try:
        Rule("R_BAD_CONC", "Bad Conclusion", (Pattern("step", "?A", "?B"),), Pattern("step", "", "?B"))
        d8_ok = False
    except ValidationError:
        d8_ok = True
    suite_results.append(("D8. Rechazo de Conclusión Incompleta en Rule", d8_ok, "Rule rechaza conclusión con source/target vacío."))

    # D9: Relation derived sin rule_id
    try:
        Relation(id="r_derived_bad", source="a", predicate="p", target="b", origin="derived", rule_id=None)
        d9_ok = False
    except ValidationError:
        d9_ok = True
    suite_results.append(("D9. Relation derived requiere rule_id", d9_ok, "Se rechaza derived sin rule_id."))

    # D10: Relation asserted con rule_id
    try:
        Relation(id="r_asserted_bad", source="a", predicate="p", target="b", origin="asserted", rule_id="R1")
        d10_ok = False
    except ValidationError:
        d10_ok = True
    suite_results.append(("D10. Relation asserted no lleva rule_id", d10_ok, "Se rechaza asserted con rule_id."))

    # D11: premises con cadena vacía
    try:
        Relation(id="r_premises_bad", source="a", predicate="p", target="b", origin="derived", rule_id="R1", premises=("r_valid", ""))
        d11_ok = False
    except ValidationError:
        d11_ok = True
    suite_results.append(("D11. premises sin cadenas vacías", d11_ok, "Se rechazan premises con cadenas vacías."))

    # D12: saturate con Rules duplicados
    k_d12 = Kernel()
    k_d12.transition(Transition("add_object", {"id": "a", "type": "N"}))
    engine12 = EngineD(k_d12)
    try:
        engine12.saturate([rule_trans, rule_trans])
        d12_ok = False
    except ValidationError:
        d12_ok = True
    suite_results.append(("D12. saturate Rechaza Rules Duplicadas", d12_ok, "saturate valida unicidad de Rule IDs."))

    # D13: Punto Fijo de Saturación
    k_d13 = Kernel()
    for o in ["a", "b", "c"]: k_d13.transition(Transition("add_object", {"id": o, "type": "N"}))
    k_d13.transition(Transition("add_relation", {"id": "R_AB", "source": "a", "predicate": "step", "target": "b"}))
    k_d13.transition(Transition("add_relation", {"id": "R_BC", "source": "b", "predicate": "step", "target": "c"}))
    
    engine13 = EngineD(k_d13)
    count13_first = engine13.saturate([rule_trans])
    count13_second = engine13.saturate([rule_trans])
    
    d13_ok = (count13_first == 1) and (count13_second == 0)
    suite_results.append(("D13. Punto Fijo de Saturación", d13_ok, "D(S*,R) = S*: segunda saturación produce 0 nuevas relaciones."))

    # D14-D15: verify_derivation — reincorporado tras pruebas cruzadas.
    # Se confirmó que, sin esto, una relación con rule_id y premises reales
    # pero conclusión falsa se acepta sin objeción y nada la detecta después.
    k_d14 = Kernel()
    for o in ["a", "b", "c", "z"]:
        k_d14.transition(Transition("add_object", {"id": o, "type": "N"}))
    k_d14.transition(Transition("add_relation", {"id": "R_AB", "source": "a", "predicate": "step", "target": "b"}))
    k_d14.transition(Transition("add_relation", {"id": "R_BC", "source": "b", "predicate": "step", "target": "c"}))
    engine14 = EngineD(k_d14)
    rule_trans14 = Rule("R_TRANS14", "Transitivity", (Pattern("step", "?A", "?B"), Pattern("step", "?B", "?C")), Pattern("step", "?A", "?C"))
    engine14.saturate([rule_trans14])
    real_derived_d14 = next(r for r in k_d14.state.relations.values() if r.origin == "derived")
    d14_ok = engine14.verify_derivation(real_derived_d14, {"R_TRANS14": rule_trans14})
    suite_results.append((
        "D14. verify_derivation Acepta una Derivación Auténtica", d14_ok,
        "Una relación genuinamente producida por saturate() se verifica como válida al re-unificar sus premisas."
    ))

    # D15: conclusión "forjada" — regla real, premises reales y existentes,
    # pero conclusión que esa regla+esas premisas NO producirían (elegida
    # para no coincidir con ningún hecho preexistente, aislando el efecto
    # de verify_derivation del de I4).
    k_d14.transition(Transition("add_relation", {
        "id": "FORGED_D15", "source": "a", "predicate": "step", "target": "z",
        "origin": "derived", "rule_id": "R_TRANS14", "premises": ("R_AB", "R_BC")
    }))
    forged_d15 = k_d14.state.relations["FORGED_D15"]
    kernel_accepted_forgery = True  # llegó hasta aquí sin excepción => el Kernel la admitió
    audit_rejects_it = not engine14.verify_derivation(forged_d15, {"R_TRANS14": rule_trans14})
    d15_ok = kernel_accepted_forgery and audit_rejects_it
    suite_results.append((
        "D15. verify_derivation Detecta una Derivación Forjada", d15_ok,
        "El Kernel admite la relación (no conoce Rules), pero verify_derivation re-unifica premisas+regla y detecta que la conclusión declarada no coincide con la que realmente producirían."
    ))

    # ------------------------------------------------------------
    # GRUPO E: PROYECCIÓN π
    # ------------------------------------------------------------

    # E1: Equivalencia bajo π_M
    k_e1 = Kernel()
    k_e2 = Kernel()
    for o in ["1", "2"]:
        k_e1.transition(Transition("add_object", {"id": o, "type": "N"}))
        k_e2.transition(Transition("add_object", {"id": o, "type": "N"}))
    
    k_e1.transition(Transition("add_relation", {"id": "ID_A", "source": "1", "predicate": "link", "target": "2"}))
    k_e2.transition(Transition("add_relation", {"id": "ID_B", "source": "1", "predicate": "link", "target": "2"}))
    
    pi_1 = project_pi(k_e1.state)
    pi_2 = project_pi(k_e2.state)
    
    e1_ok = (pi_1 == pi_2) and (k_e1.state != k_e2.state)
    suite_results.append(("E1. Equivalencia bajo π_M", e1_ok, "π_M ignora IDs operacionales (proyección parcial)."))

    # E2: π_M ignora metadatos operacionales (origin, rule_id, premises)
    k_e3 = Kernel()
    k_e4 = Kernel()
    for o in ["x", "y"]:
        k_e3.transition(Transition("add_object", {"id": o, "type": "N"}))
        k_e4.transition(Transition("add_object", {"id": o, "type": "N"}))
    
    k_e3.transition(Transition("add_relation", {
        "id": "R_ASSERTED", "source": "x", "predicate": "p", "target": "y",
        "origin": "asserted"
    }))
    
    k_e4.transition(Transition("add_relation", {
        "id": "R_DERIVED", "source": "x", "predicate": "p", "target": "y",
        "origin": "derived", "rule_id": "R1", "premises": ()
    }))
    
    pi_3 = project_pi(k_e3.state)
    pi_4 = project_pi(k_e4.state)
    
    e2_ok = (pi_3 == pi_4)
    suite_results.append(("E2. π_M Ignora Metadatos Operacionales", e2_ok, "π_M elimina origin, rule_id y premises."))

    # E3: Determinismo de π_M
    k_e5 = Kernel()
    for o in ["a", "b"]: k_e5.transition(Transition("add_object", {"id": o, "type": "N"}))
    k_e5.transition(Transition("add_relation", {"id": "r1", "source": "a", "predicate": "p", "target": "b"}))
    
    pi_first = project_pi(k_e5.state)
    pi_second = project_pi(k_e5.state)
    
    e3_ok = (pi_first == pi_second)
    suite_results.append(("E3. Determinismo de π_M", e3_ok, "π_M(S) produce el mismo resultado para el mismo estado."))

    # E4-E6: ~π como relación de equivalencia formal, usando states_equivalent()
    # (reincorporado tras pruebas cruzadas: antes solo había comparaciones ad
    # hoc "pi_1 == pi_2" sueltas, sin una función nombrada ni prueba explícita
    # de reflexividad/transitividad/poder discriminante).

    e4_ok = states_equivalent(k_e1.state, k_e1.state)
    suite_results.append(("E4. Reflexividad de ~π", e4_ok, "Todo estado es ~π-equivalente a sí mismo."))

    k_e6 = Kernel()
    for o in ["1", "2"]:
        k_e6.transition(Transition("add_object", {"id": o, "type": "N"}))
    k_e6.transition(Transition("add_relation", {"id": "ID_C_TRANSITIVE", "source": "1", "predicate": "link", "target": "2"}))
    e5_ok = states_equivalent(k_e1.state, k_e2.state) and states_equivalent(k_e2.state, k_e6.state) and states_equivalent(k_e1.state, k_e6.state)
    suite_results.append(("E5. Transitividad de ~π", e5_ok, "s1 ~π s2 y s2 ~π s3 implican s1 ~π s3 (probado con tres estados de IDs distintos)."))

    k_e7 = Kernel()
    for o in ["1", "2"]:
        k_e7.transition(Transition("add_object", {"id": o, "type": "N"}))
    k_e7.transition(Transition("add_relation", {"id": "ID_D_DIFFERENT", "source": "1", "predicate": "otra_relacion", "target": "2"}))
    e6_ok = not states_equivalent(k_e1.state, k_e7.state)
    suite_results.append(("E6. Poder Discriminante de ~π", e6_ok, "Dos estados con contenido relacional distinto NO son ~π-equivalentes (states_equivalent no es trivialmente verdadera)."))

    # ------------------------------------------------------------
    # GRUPO F: ARQUITECTURA Y REPRESENTABILIDAD
    # ------------------------------------------------------------

    # F1: Representación estructural del núcleo y consistencia
    k_f = Kernel()
    for comp in ["COMP_O", "COMP_M", "COMP_A", "COMP_DELTA"]:
        k_f.transition(Transition("add_object", {"id": comp, "type": "Primitive"}))
    k_f.transition(Transition("add_object", {"id": "ARCH_SPEC", "type": "Spec"}))
    
    for comp in ["COMP_O", "COMP_M", "COMP_A", "COMP_DELTA"]:
        k_f.transition(Transition("add_relation", {"id": f"LINK_{comp}", "source": "ARCH_SPEC", "predicate": "has_part", "target": comp}))

    k_f.transition(Transition("add_axiom", {
        "id": "AX_NO_ERRORS", "name": "StrictConsistency",
        "body": ({"predicate": "has_error", "source": "?S", "target": "?E", "polarity": True},)
    }))

    try:
        k_f.transition(Transition("add_object", {"id": "ERR_FLAG", "type": "Error"}))
        k_f.transition(Transition("add_relation", {"id": "R_ERR", "source": "ARCH_SPEC", "predicate": "has_error", "target": "ERR_FLAG"}))
        f_ok = False
    except ContradictionError:
        f_ok = True
        
    suite_results.append(("F1. Representación Estructural del Núcleo", f_ok, "El Kernel puede representar su propia arquitectura como datos y validarla."))

    # F2: Autorrepresentación formal de la completitud de las 4 primitivas
    # (reincorporada tras pruebas cruzadas: F1 arriba prueba que el Kernel
    # puede representar SU arquitectura como datos, pero no específicamente
    # que la COMPLETITUD de O,M,A,δ sea detectable dentro del propio
    # formalismo sin apoyo de una función Python externa — que era el punto
    # concreto de la auditoría original. Se confirmó que este motor de
    # cláusulas SÍ soporta el escenario; solo faltaba la prueba.)
    #
    # La "ausencia" de una primitiva se representa como NEGACIÓN EXPLÍCITA de
    # composed_of (nunca como borrado físico, invisible a un axioma de
    # patrones +/-). Un único axioma con variable compartida (?C) entre
    # is_primitive(+) y composed_of(-) permite que el propio EvaluatorA
    # detecte la violación, sin ninguna función externa.
    k_f2 = Kernel()
    k_f2.transition(Transition("add_object", {"id": "ARCH_SPEC", "type": "Metamodel"}))
    for comp in ["COMP_O", "COMP_M", "COMP_A", "COMP_DELTA"]:
        k_f2.transition(Transition("add_object", {"id": comp, "type": "Primitive"}))
        k_f2.transition(Transition("add_relation", {
            "id": f"IS_PRIM_{comp}", "source": "ARCH_SPEC", "predicate": "is_primitive", "target": comp, "polarity": True
        }))
        k_f2.transition(Transition("add_relation", {
            "id": f"LINK_{comp}", "source": "ARCH_SPEC", "predicate": "composed_of", "target": comp, "polarity": True
        }))
    k_f2.transition(Transition("add_axiom", {
        "id": "AX_FOUR_PRIMITIVES", "name": "CompletitudDeLasCuatroPrimitivas",
        "body": [
            {"predicate": "is_primitive", "source": "ARCH_SPEC", "target": "?C", "polarity": True},
            {"predicate": "composed_of", "source": "ARCH_SPEC", "target": "?C", "polarity": False},
        ]
    }))
    f2_valid_with_four = True
    try:
        Validator().validate(k_f2.state)
    except ContradictionError:
        f2_valid_with_four = False

    # Paso A: borrado FÍSICO — deliberadamente insuficiente (no hay
    # negación-como-falla). El estado debe seguir siendo válido.
    k_f2.transition(Transition("remove_relation", {"id": "LINK_COMP_DELTA"}))
    f2_deletion_alone_insufficient = True
    try:
        Validator().validate(k_f2.state)
    except ContradictionError:
        f2_deletion_alone_insufficient = False

    # Paso B: negación EXPLÍCITA — ahora sí, el propio axioma (evaluado
    # enteramente dentro del Kernel) detona la contradicción.
    snapshot_f2 = k_f2.state
    f2_detected_by_axiom = False
    try:
        k_f2.transition(Transition("add_relation", {
            "id": "NEGATE_COMP_DELTA", "source": "ARCH_SPEC", "predicate": "composed_of",
            "target": "COMP_DELTA", "polarity": False
        }))
    except ContradictionError:
        f2_detected_by_axiom = True

    f2_ok = (
        f2_valid_with_four and f2_deletion_alone_insufficient and f2_detected_by_axiom
        and (k_f2.state == snapshot_f2) and ("NEGATE_COMP_DELTA" not in k_f2.state.relations)
    )
    suite_results.append((
        "F2. Autorrepresentación Formal de la Completitud de las 4 Primitivas", f2_ok,
        "El borrado físico del enlace es insuficiente para disparar el axioma; la negación explícita de una primitiva obligatoria SÍ es detectada como contradicción por el propio Kernel, sin función de auditoría externa."
    ))

    # ------------------------------------------------------------
    # GRUPO G: INDEPENDENCIA OPERACIONAL
    # ------------------------------------------------------------
    # NOTA METODOLÓGICA (añadida tras pruebas cruzadas): G1-G5 demuestran
    # INDEPENDENCIA OPERACIONAL entre las primitivas -- no irreductibilidad
    # matemática en el sentido fuerte, que exigiría exhibir una reducción
    # explícita de una primitiva a las demás y demostrar que alguna
    # propiedad deseada deja de ser representable. G6 sí ofrece un
    # argumento de irreductibilidad genuina, pero deliberadamente acotado a
    # una sola primitiva (O). La irreductibilidad de M, A y δ se deja
    # explícitamente fuera de alcance (ver certificado final): extenderla
    # es un programa de trabajo propio, no una corrección pendiente.

    # G1: Identidad Discreta O
    k_g1 = Kernel()
    k_g1.transition(Transition("add_object", {"id": "t1", "type": "T", "value": 10}))
    k_g1.transition(Transition("add_object", {"id": "t2", "type": "T", "value": 10}))
    g1_ok = (k_g1.state.objects["t1"] is not k_g1.state.objects["t2"])
    suite_results.append(("G1. Identidad Discreta O", g1_ok, "Objetos con mismo valor mantienen identidad distinta."))

    # G2: Independencia M
    k_g2 = Kernel()
    k_g2.transition(Transition("add_object", {"id": "n1", "type": "N"}))
    k_g2.transition(Transition("add_relation", {"id": "r1", "source": "n1", "predicate": "e", "target": "n1"}))
    k_g2.transition(Transition("remove_relation", {"id": "r1"}))
    g2_ok = ("n1" in k_g2.state.objects and "r1" not in k_g2.state.relations)
    suite_results.append(("G2. Independencia M", g2_ok, "Eliminar relación no afecta objetos."))

    # G3: Autoridad de A
    k_g3 = Kernel()
    k_g3.transition(Transition("add_object", {"id": "x", "type": "X"}))
    k_g3.transition(Transition("add_axiom", {"id": "AX_IRR", "name": "Irreflexive", "body": ({"predicate": "self", "source": "?X", "target": "?X", "polarity": True},)}))
    g3_ok = False
    try:
        k_g3.transition(Transition("add_relation", {"id": "r_self", "source": "x", "predicate": "self", "target": "x"}))
    except ContradictionError:
        g3_ok = True
    suite_results.append(("G3. Autoridad de A", g3_ok, "Axiomas vetan configuraciones relacionales."))

    # G4: Preservación del estado ante rechazo
    k_g4 = Kernel()
    k_g4.transition(Transition("add_object", {"id": "base", "type": "B"}))
    s_pre = k_g4.state
    try:
        k_g4.transition(Transition("add_object", {"id": "base", "type": "B"}))
    except KernelError:
        pass
    g4_ok = (k_g4.state == s_pre)
    suite_results.append(("G4. Preservación del Estado ante Rechazo", g4_ok, "Transición rechazada no modifica el estado."))

    # G5: Identidad vs Igualdad Semántica en O
    obj1 = Object(id="x1", type="N", value=5)
    obj2 = Object(id="x2", type="N", value=5)
    g5_ok = (obj1 != obj2) and (obj1.value == obj2.value)
    suite_results.append(("G5. Identidad vs Igualdad Semántica", g5_ok, "La identidad de O está determinada por ID; igualdad de valor no implica identidad."))

    # G6: Argumento de irreductibilidad GENUINA — acotado a O (reincorporado
    # tras pruebas cruzadas). A diferencia de G1-G5 (independencia
    # operacional), esto exhibe una capacidad expresiva que pertenece
    # EXCLUSIVAMENTE al esquema de O y que no puede codificarse mediante M o
    # A, por construcción de sus propios esquemas de datos:
    #   - Relation no posee ningún campo de carga escalar (solo id, source,
    #     predicate, target, polarity, origin, rule_id, premises) — no hay
    #     dónde almacenar un valor sujeto a restricción de rango numérico.
    #   - AxiomConstraint.numeric_target_type se evalúa EXCLUSIVAMENTE
    #     contra obj.type/obj.value para obj en state.objects — no existe
    #     ruta equivalente sobre state.relations.
    # Por tanto, la invariante numérica (bool/NaN/Inf/rango) es, por
    # construcción del esquema, irrepresentable si se elimina O.
    import dataclasses as _dc
    relation_field_names = {f.name for f in _dc.fields(Relation)}
    axiom_field_names = {f.name for f in _dc.fields(AxiomConstraint)}
    object_field_names = {f.name for f in _dc.fields(Object)}
    g6_relation_has_no_scalar_payload = "value" not in relation_field_names
    g6_axiom_numeric_channel_exists = "numeric_target_type" in axiom_field_names
    g6_object_has_typed_scalar_payload = {"type", "value"}.issubset(object_field_names)
    g6_ok = g6_relation_has_no_scalar_payload and g6_axiom_numeric_channel_exists and g6_object_has_typed_scalar_payload
    suite_results.append((
        "G6. Irreductibilidad Genuina de O (acotada; M/A/δ fuera de alcance)", g6_ok,
        "La capacidad de portar un valor escalar tipado sujeto a restricción numérica pertenece exclusivamente al esquema de Object: Relation no tiene campo de carga numérica, y AxiomConstraint solo evalúa contra state.objects — por construcción del esquema, no por convención de uso."
    ))

    # ------------------------------------------------------------
    # GRUPO H: HARDENING FINAL
    # ------------------------------------------------------------

    # H1: Inmutabilidad profunda
    k_h1 = Kernel()
    props = {"key": "value"}
    k_h1.transition(Transition("add_object", {"id": "obj", "type": "T", "properties": props}))
    
    # Modificar el diccionario original
    props["key"] = "modified"
    props["new_key"] = "new_value"
    
    # El estado no debe haber cambiado
    h1_ok = (k_h1.state.objects["obj"].properties["key"] == "value") and ("new_key" not in k_h1.state.objects["obj"].properties)
    suite_results.append(("H1. Inmutabilidad Profunda", h1_ok, "Modificar estructuras originales no altera el estado."))

    # H2: Identidad del estado
    k_h2 = Kernel()
    k_h2.transition(Transition("add_object", {"id": "x", "type": "X"}))
    s_before = k_h2.state
    k_h2.transition(Transition("add_object", {"id": "y", "type": "Y"}))
    s_after = k_h2.state
    
    h2_ok = (s_before is not s_after) and (s_before != s_after)
    suite_results.append(("H2. Identidad del Estado", h2_ok, "Transición válida produce S_antes ≠ S_después."))

    # H3: Atomicidad universal
    k_h3 = Kernel()
    k_h3.transition(Transition("add_object", {"id": "a", "type": "A"}))
    
    # Intentar múltiples transiciones inválidas
    s_initial = k_h3.state
    for i in range(5):
        try:
            k_h3.transition(Transition("add_object", {"id": "a", "type": "A"}))  # duplicado
        except DuplicateIDError:
            pass
    
    h3_ok = (k_h3.state == s_initial)
    suite_results.append(("H3. Atomicidad Universal", h3_ok, "Toda transición rechazada conserva S'=S."))

    # H4: Invariante de validez
    k_h4 = Kernel()
    k_h4.transition(Transition("add_object", {"id": "x", "type": "X"}))
    k_h4.transition(Transition("add_object", {"id": "y", "type": "Y"}))
    k_h4.transition(Transition("add_relation", {"id": "r1", "source": "x", "predicate": "p", "target": "y"}))
    k_h4.transition(Transition("add_axiom", {"id": "ax1", "name": "Test"}))
    
    # Verificar que el estado final es válido
    h4_ok = True
    try:
        k_h4.validator.validate(k_h4.state)
    except Exception:
        h4_ok = False
    
    suite_results.append(("H4. Invariante de Validez", h4_ok, "Toda transición aceptada produce Validator(S')=OK."))

    # H5: Punto fijo de saturación (confirmación)
    k_h5 = Kernel()
    for o in ["a", "b"]: k_h5.transition(Transition("add_object", {"id": o, "type": "N"}))
    k_h5.transition(Transition("add_relation", {"id": "R_AB", "source": "a", "predicate": "step", "target": "b"}))
    
    engine_h5 = EngineD(k_h5)
    rule_simple = Rule("R_ID", "Identity",
                       (Pattern("step", "?A", "?B"),),
                       Pattern("step", "?A", "?B"))
    
    count_h5_first = engine_h5.saturate([rule_simple])
    count_h5_second = engine_h5.saturate([rule_simple])
    
    h5_ok = (count_h5_first >= 0) and (count_h5_second == 0)
    suite_results.append(("H5. Punto Fijo de Saturación (Confirmación)", h5_ok, "D(S*,R) = S*."))

    # H6: Estabilidad de π_M
    k_h6 = Kernel()
    for o in ["x", "y"]: k_h6.transition(Transition("add_object", {"id": o, "type": "N"}))
    k_h6.transition(Transition("add_relation", {"id": "r1", "source": "x", "predicate": "p", "target": "y"}))
    
    pi_h6_first = project_pi(k_h6.state)
    pi_h6_second = project_pi(k_h6.state)
    
    h6_ok = (pi_h6_first == pi_h6_second)
    suite_results.append(("H6. Estabilidad de π_M", h6_ok, "π_M(S) es estable bajo llamadas repetidas."))

    # H7: Preservación ante violación semántica
    k_h7 = Kernel()
    k_h7.transition(Transition("add_object", {"id": "a", "type": "N"}))
    k_h7.transition(Transition("add_object", {"id": "b", "type": "N"}))
    k_h7.transition(Transition("add_axiom", {
        "id": "AX_NO_LINK", "name": "NoLinkAllowed",
        "body": ({"predicate": "link", "source": "?X", "target": "?Y", "polarity": True},)
    }))
    
    # Estado antes de intentar transición inválida
    s_before_h7 = k_h7.state
    
    # Intentar agregar relación que viola axioma
    h7_ok = False
    try:
        k_h7.transition(Transition("add_relation", {"id": "r_link", "source": "a", "predicate": "link", "target": "b"}))
    except ContradictionError:
        # Verificar que el estado no cambió
        h7_ok = (k_h7.state == s_before_h7) and ("r_link" not in k_h7.state.relations)
    
    suite_results.append(("H7. Preservación ante Violación Semántica", h7_ok, "Axioma detonado preserva estado anterior intacto."))

    # H8: Inmutabilidad de State.objects
    objects_dict = {}
    state_h8 = State(objects=objects_dict)
    objects_dict["x"] = Object(id="x", type="T")
    h8_ok = "x" not in state_h8.objects
    suite_results.append(("H8. Inmutabilidad de State.objects", h8_ok, "Modificar dict original no afecta State."))

    # H9: Inmutabilidad de Transition.payload
    payload_h9 = {"id": "x", "type": "T"}
    t_h9 = Transition("add_object", payload_h9)
    payload_h9["id"] = "mal"
    h9_ok = t_h9.payload["id"] == "x"
    suite_results.append(("H9. Inmutabilidad de Transition.payload", h9_ok, "Modificar payload original no afecta Transition."))

    # H10: Inmutabilidad de Relation.premises
    premises_list = ["r1", "r2"]
    rel_h10 = Relation(id="r", source="a", predicate="p", target="b", origin="derived", rule_id="R1", premises=premises_list)
    premises_list.append("r3")
    h10_ok = len(rel_h10.premises) == 2
    suite_results.append(("H10. Inmutabilidad de Relation.premises", h10_ok, "Modificar lista original no afecta Relation.premises."))

    # H11: Relation derived con rule_id vacío
    try:
        Relation(id="r_empty", source="a", predicate="p", target="b", origin="derived", rule_id="")
        h11_ok = False
    except ValidationError:
        h11_ok = True
    suite_results.append(("H11. Relation derived rechaza rule_id vacío", h11_ok, "Se rechaza derived con rule_id=''."))

    # H12: Filosofía A — CONTRADICTION es inalcanzable vía δ (reincorporado
    # tras pruebas cruzadas). El docstring de query_evidence ya declaraba
    # esta postura, pero no existía una prueba dedicada que la verificara:
    # todo intento de construir, vía Kernel.transition, un estado con ambas
    # polaridades del mismo triple debe ser rechazado por I3 — de modo que
    # query_evidence() nunca observe "CONTRADICTION" para un estado
    # alcanzado exclusivamente por δ.
    k_h12 = Kernel()
    k_h12.transition(Transition("add_object", {"id": "Xh12", "type": "T"}))
    k_h12.transition(Transition("add_object", {"id": "Yh12", "type": "T"}))
    k_h12.transition(Transition("add_relation", {"id": "Rh12_1", "source": "Xh12", "predicate": "rel", "target": "Yh12", "polarity": True}))
    engine_h12 = EngineD(k_h12)
    status_before_h12 = engine_h12.query_evidence("Xh12", "rel", "Yh12")
    h12_blocked = False
    try:
        k_h12.transition(Transition("add_relation", {"id": "Rh12_2", "source": "Xh12", "predicate": "rel", "target": "Yh12", "polarity": False}))
    except ContradictionError:
        h12_blocked = True
    status_after_h12 = engine_h12.query_evidence("Xh12", "rel", "Yh12")
    h12_ok = (status_before_h12 == "TRUE") and h12_blocked and (status_after_h12 == "TRUE") and (status_after_h12 != "CONTRADICTION")
    suite_results.append((
        "H12. CONTRADICTION es Inalcanzable vía δ (Filosofía A)", h12_ok,
        "Todo intento de construir, vía Kernel.transition, un estado con ambas polaridades del mismo triple es rechazado por I3; query_evidence() nunca observa CONTRADICTION para un estado alcanzado exclusivamente por δ."
    ))

    # ------------------------------------------------------------
    # GRUPO I: EXTENSIONES (persistencia, rendimiento, concurrencia, uso)
    # ------------------------------------------------------------

    # I1: Persistencia — ciclo completo guardar/cargar preserva el contenido
    import tempfile, os
    k_i1 = Kernel()
    k_i1.transition(Transition("add_object", {"id": "px", "type": "Persona", "value": 42, "properties": {"nombre": "Ana", "tags": [1, 2, 3]}}))
    k_i1.transition(Transition("add_object", {"id": "py", "type": "Persona"}))
    k_i1.transition(Transition("add_relation", {"id": "R_I1", "source": "px", "predicate": "conoce", "target": "py"}))
    k_i1.transition(Transition("add_axiom", {
        "id": "AX_I1", "name": "SinAutorreferencia",
        "body": [{"predicate": "conoce", "source": "?X", "target": "?X", "polarity": True}]
    }))
    with tempfile.TemporaryDirectory() as tmpdir:
        path_i1 = os.path.join(tmpdir, "estado.json")
        save_state(k_i1.state, path_i1)
        loaded_state_i1 = load_state(path_i1)
        k_i1_loaded = Kernel(loaded_state_i1)  # debe validar sin excepcion
        i1_ok = (
            states_equivalent(k_i1.state, k_i1_loaded.state)
            and k_i1_loaded.state.objects["px"].value == 42
            and k_i1_loaded.state.objects["px"].properties["nombre"] == "Ana"
            and list(k_i1_loaded.state.objects["px"].properties["tags"]) == [1, 2, 3]
            and len(k_i1_loaded.state.axioms) == 1
        )
    suite_results.append((
        "I1. Persistencia: ciclo guardar/cargar preserva objetos, relaciones y axiomas", i1_ok,
        "save_state()+load_state() reconstruyen un State ~π-equivalente, con valores y propiedades anidadas intactos, que valida correctamente al construir un Kernel."
    ))

    # I2: Persistencia — el estado cargado sigue siendo un Kernel funcional
    # (puede recibir nuevas transiciones y seguir validando)
    i2_ok = False
    try:
        k_i1_loaded.transition(Transition("add_relation", {"id": "R_I2_NUEVA", "source": "py", "predicate": "conoce", "target": "px"}))
        i2_ok = "R_I2_NUEVA" in k_i1_loaded.state.relations
    except Exception:
        i2_ok = False
    suite_results.append((
        "I2. Persistencia: el Kernel reconstruido admite nuevas transiciones", i2_ok,
        "Un Kernel construido desde un estado cargado de disco sigue operando con normalidad (no es una copia inerte)."
    ))

    # I3: Rendimiento — saturate() con salvaguarda max_total_derived aborta
    # con un error claro ante crecimiento combinatorio, en vez de colgarse.
    k_i3 = Kernel()
    for i in range(30):
        k_i3.transition(Transition("add_object", {"id": f"ci{i}", "type": "N"}))
    for i in range(29):
        k_i3.transition(Transition("add_relation", {"id": f"cr{i}", "source": f"ci{i}", "predicate": "step", "target": f"ci{i+1}"}))
    engine_i3 = EngineD(k_i3)
    rule_i3 = Rule("R_TRANS_I3", "T", (Pattern("step", "?A", "?B"), Pattern("step", "?B", "?C")), Pattern("step", "?A", "?C"))
    i3_ok = False
    try:
        engine_i3.saturate([rule_i3], max_total_derived=50)
    except InvalidTransitionError:
        i3_ok = True
    suite_results.append((
        "I3. saturate() con max_total_derived aborta ante crecimiento combinatorio", i3_ok,
        "En vez de colgarse silenciosamente ante una regla que genera cierre transitivo O(n²), saturate() aborta con un error accionable al superar el límite explícito."
    ))

    # I4: Rendimiento — el índice no cambia el resultado semántico frente al
    # cálculo de referencia (mismo escenario que D1, verificado de nuevo
    # aquí específicamente para descartar que indexar haya alterado algo).
    k_i4 = Kernel()
    for o in ["Q1", "Q2", "Q3", "Q4"]:
        k_i4.transition(Transition("add_object", {"id": o, "type": "N"}))
    k_i4.transition(Transition("add_relation", {"id": "QR1", "source": "Q1", "predicate": "step", "target": "Q2"}))
    k_i4.transition(Transition("add_relation", {"id": "QR2", "source": "Q2", "predicate": "step", "target": "Q3"}))
    k_i4.transition(Transition("add_relation", {"id": "QR3", "source": "Q3", "predicate": "step", "target": "Q4"}))
    engine_i4 = EngineD(k_i4)
    rule_i4 = Rule("R_TRANS_I4", "T", (Pattern("step", "?A", "?B"), Pattern("step", "?B", "?C")), Pattern("step", "?A", "?C"))
    engine_i4.saturate([rule_i4])
    expected_pairs = {("Q1", "Q3"), ("Q2", "Q4"), ("Q1", "Q4")}
    got_pairs = {(r.source, r.target) for r in k_i4.state.relations.values() if r.origin == "derived"}
    i4_ok = (got_pairs == expected_pairs)
    suite_results.append((
        "I4. El índice interno de EngineD produce el mismo resultado que el cálculo directo", i4_ok,
        f"Cierre transitivo esperado sobre una cadena de 4 nodos: {sorted(expected_pairs)}; obtenido: {sorted(got_pairs)}."
    ))

    # I5: Concurrencia — sin sincronización, transiciones concurrentes
    # pueden perder actualizaciones (se documenta el riesgo, no se exige
    # reproducirlo de forma determinista: depende del entrelazado real de
    # hilos). Lo que SÍ se prueba de forma determinista es que
    # ThreadSafeKernel, bajo la misma carga concurrente, no pierde ninguna.
    import concurrent.futures

    def _hammer(kernel_like, prefix, n):
        for i in range(n):
            kernel_like.transition(Transition("add_object", {"id": f"{prefix}_{i}", "type": "N"}))

    k_i5 = ThreadSafeKernel()
    n_threads, n_per_thread = 12, 15
    with concurrent.futures.ThreadPoolExecutor(max_workers=n_threads) as pool:
        futures = [pool.submit(_hammer, k_i5, f"t{t}", n_per_thread) for t in range(n_threads)]
        for f in futures:
            f.result()
    i5_ok = (len(k_i5.state.objects) == n_threads * n_per_thread)
    suite_results.append((
        "I5. ThreadSafeKernel no pierde actualizaciones bajo concurrencia real", i5_ok,
        f"Se esperaban {n_threads * n_per_thread} objetos desde {n_threads} hilos concurrentes; se obtuvieron {len(k_i5.state.objects)}."
    ))

    # I6: Capa de uso — MFMin produce EXACTAMENTE el mismo estado (vía π y
    # conteo) que las llamadas equivalentes a Kernel/Transition crudas.
    mf_i6 = MFMin()
    mf_i6.add_object("a", "N").add_object("b", "N").add_relation("r1", "a", "vinculo", "b")
    mf_i6.add_axiom("AX_I6", "SinAuto", body=[("vinculo", "?X", "?X", True)])

    k_ref_i6 = Kernel()
    k_ref_i6.transition(Transition("add_object", {"id": "a", "type": "N"}))
    k_ref_i6.transition(Transition("add_object", {"id": "b", "type": "N"}))
    k_ref_i6.transition(Transition("add_relation", {"id": "r1", "source": "a", "predicate": "vinculo", "target": "b"}))
    k_ref_i6.transition(Transition("add_axiom", {
        "id": "AX_I6", "name": "SinAuto",
        "body": [{"predicate": "vinculo", "source": "?X", "target": "?X", "polarity": True}]
    }))
    i6_ok = (
        states_equivalent(mf_i6.state, k_ref_i6.state)
        and len(mf_i6.state.axioms) == len(k_ref_i6.state.axioms)
        and mf_i6.query("a", "vinculo", "b") == "TRUE"
    )
    suite_results.append((
        "I6. MFMin (capa de uso) produce el mismo estado que Kernel/Transition crudos", i6_ok,
        "La fachada no altera semántica: arma los mismos payloads y delega, verificado por equivalencia de estado."
    ))

    # I7: Capa de uso — encadenamiento fluido + guardar/cargar por la fachada
    with tempfile.TemporaryDirectory() as tmpdir2:
        path_i7 = os.path.join(tmpdir2, "mf.json")
        mf_i6.save(path_i7)
        mf_i7_loaded = MFMin.load(path_i7)
        i7_ok = states_equivalent(mf_i6.state, mf_i7_loaded.state) and mf_i7_loaded.query("a", "vinculo", "b") == "TRUE"
    suite_results.append((
        "I7. MFMin.save()/MFMin.load() end-to-end", i7_ok,
        "La fachada expone persistencia sin exponer Kernel/State directamente al usuario final."
    ))

    # I8: Persistencia de Rule/Pattern — antes solo se persistía State (O,M,A);
    # las reglas del motor D no tenían forma de guardarse/cargarse.
    rule_i8 = Rule("R_TRANS_I8", "Transitividad",
                    (Pattern("step", "?A", "?B"), Pattern("step", "?B", "?C")),
                    Pattern("step", "?A", "?C"))
    with tempfile.TemporaryDirectory() as tmpdir3:
        path_rules = os.path.join(tmpdir3, "rules.json")
        save_rules([rule_i8], path_rules)
        loaded_rules = load_rules(path_rules)
    i8_ok = (
        len(loaded_rules) == 1
        and loaded_rules[0].id == "R_TRANS_I8"
        and loaded_rules[0].premises == rule_i8.premises
        and loaded_rules[0].conclusion == rule_i8.conclusion
    )
    suite_results.append((
        "I8. Persistencia de Rule/Pattern (save_rules/load_rules)", i8_ok,
        "Una regla de inferencia sobrevive un ciclo guardar/cargar con premisas y conclusión idénticas."
    ))

    # I9: MFMin persiste hechos + axiomas + reglas como un conjunto único, y
    # el resultado cargado puede seguir derivando con las mismas reglas sin
    # tener que redefinirlas en código.
    mf_i9 = MFMin()
    mf_i9.add_object("j1", "N").add_object("j2", "N").add_object("j3", "N")
    mf_i9.add_relation("jr1", "j1", "step", "j2").add_relation("jr2", "j2", "step", "j3")
    mf_i9.add_rule(Rule("R_TRANS_I9", "T", (Pattern("step", "?A", "?B"), Pattern("step", "?B", "?C")), Pattern("step", "?A", "?C")))
    with tempfile.TemporaryDirectory() as tmpdir4:
        path_i9 = os.path.join(tmpdir4, "mf9.json")
        mf_i9.save(path_i9)
        mf_i9_loaded = MFMin.load(path_i9)
        rules_survived = len(mf_i9_loaded.rules) == 1 and mf_i9_loaded.rules[0].id == "R_TRANS_I9"
        n_derived_i9 = mf_i9_loaded.derive()  # usa self.rules, cargadas de disco, no pasadas de nuevo en codigo
        i9_ok = rules_survived and n_derived_i9 == 1 and mf_i9_loaded.query("j1", "step", "j3") == "TRUE"
    suite_results.append((
        "I9. MFMin.save()/load() persiste hechos+axiomas+reglas como un conjunto", i9_ok,
        "Tras cargar de disco, MFMin.derive() sin argumentos deriva correctamente usando las reglas recuperadas, no reglas redefinidas en código."
    ))

    # ------------------------------------------------------------
    # GRUPO J: EVALUACIÓN SEMI-INGENUA — CORRECCIÓN Y LÍMITE MEDIDO
    # ------------------------------------------------------------
    # Decisión tomada en esta sesión: reemplazar la evaluación ingenua de
    # EngineD.saturate() (reunir TODO el estado contra sí mismo en cada
    # ronda) por evaluación semi-ingenua (cada ronda exige que al menos una
    # premisa provenga de lo derivado en la ronda anterior). Es un cambio
    # de ESTRATEGIA DE EVALUACIÓN, no de semántica: el punto fijo calculado
    # debe ser IDÉNTICO. J1 lo verifica por comparación directa.

    def _naive_reference_saturate(kernel, rules, max_rounds=2000):
        """Reimplementación deliberadamente ingenua, solo para esta prueba de regresión."""
        engine_ref = EngineD(kernel)
        rounds = 0
        total_ref = 0
        while True:
            rounds += 1
            if rounds > max_rounds:
                raise InvalidTransitionError("naive_reference no convergió")
            new_rels = []
            for rule in rules:
                new_rels.extend(engine_ref.infer_step(rule, delta_ids=None))  # None = ingenua, sin restricción
            if not new_rels:
                break
            seen = {}
            for r in new_rels:
                key = (r.source, r.predicate, r.target, r.polarity)
                seen.setdefault(key, r)
            payload = tuple({"id": r.id, "source": r.source, "predicate": r.predicate, "target": r.target,
                              "polarity": r.polarity, "rule_id": r.rule_id, "premises": r.premises} for r in seen.values())
            kernel.transition(Transition("batch_derive", {"relations": payload}))
            total_ref += len(seen)
        return total_ref

    def _build_multi_path_kernel():
        """Grafo con múltiples caminos intermedios válidos entre varios pares — el caso que ejercita la deduplicación por hecho, no solo por combinación de premisas."""
        k = Kernel()
        for o in ["a", "b1", "b2", "b3", "c", "d"]:
            k.transition(Transition("add_object", {"id": o, "type": "N"}))
        k.transition(Transition("add_relation", {"id": "r_ab1", "source": "a", "predicate": "step", "target": "b1"}))
        k.transition(Transition("add_relation", {"id": "r_ab2", "source": "a", "predicate": "step", "target": "b2"}))
        k.transition(Transition("add_relation", {"id": "r_ab3", "source": "a", "predicate": "step", "target": "b3"}))
        k.transition(Transition("add_relation", {"id": "r_b1c", "source": "b1", "predicate": "step", "target": "c"}))
        k.transition(Transition("add_relation", {"id": "r_b2c", "source": "b2", "predicate": "step", "target": "c"}))
        k.transition(Transition("add_relation", {"id": "r_b3c", "source": "b3", "predicate": "step", "target": "c"}))
        k.transition(Transition("add_relation", {"id": "r_cd", "source": "c", "predicate": "step", "target": "d"}))
        return k

    rule_j = Rule("R_TRANS_J", "T", (Pattern("step", "?A", "?B"), Pattern("step", "?B", "?C")), Pattern("step", "?A", "?C"))

    k_j_semi = _build_multi_path_kernel()
    engine_j_semi = EngineD(k_j_semi)
    n_semi = engine_j_semi.saturate([rule_j])

    k_j_naive = _build_multi_path_kernel()
    n_naive = _naive_reference_saturate(k_j_naive, [rule_j])

    j1_ok = (
        project_pi(k_j_semi.state) == project_pi(k_j_naive.state)
        and n_semi == n_naive
    )
    suite_results.append((
        "J1. Evaluación semi-ingenua produce el MISMO punto fijo que la ingenua (incluso con múltiples caminos intermedios válidos entre el mismo par)",
        j1_ok,
        f"Semi-ingenua derivó {n_semi} hechos, ingenua derivó {n_naive}; π(estado) idéntico en ambos casos."
    ))

    # J2: mismo escenario que J1 pero sobre la cadena mas grande usada en
    # las mediciones de esta sesión, para no perder cobertura de ese caso
    # especifico (cierre transitivo total de una cadena), a escala moderada
    # para que la prueba siga corriendo en tiempo razonable.
    def _build_chain(n):
        k = Kernel()
        for i in range(n):
            k.transition(Transition("add_object", {"id": f"cn{i}", "type": "N"}))
        for i in range(n - 1):
            k.transition(Transition("add_relation", {"id": f"cr{i}", "source": f"cn{i}", "predicate": "step", "target": f"cn{i+1}"}))
        return k

    n_chain = 40
    k_chain = _build_chain(n_chain)
    engine_chain = EngineD(k_chain)
    total_chain = engine_chain.saturate([rule_j], max_total_derived=200_000)
    expected_chain = (n_chain - 1) * (n_chain - 2) // 2
    j2_ok = (total_chain == expected_chain)
    suite_results.append((
        "J2. Clausura transitiva completa de una cadena: cuenta exacta de hechos derivados",
        j2_ok,
        f"n={n_chain} nodos: derivados={total_chain}, esperado=(n-1)(n-2)/2={expected_chain}."
    ))

    # ------------------------------------------------------------
    # GRUPO K: COMPOSICIÓN ATÓMICA Y PROPUESTAS EXTERNAS
    # ------------------------------------------------------------
    # Responde directamente al punto más vago de la propuesta de arquitectura
    # externa evaluada en esta sesión ("el Compositor detecta conflictos"):
    # aquí se prueba el mecanismo CONCRETO (transition_batch: todo-o-nada,
    # sin resolución heurística de conflictos), y el flujo completo
    # "propone -> no autoriza -> se valida -> opcionalmente se promueve".

    # K1: transition_batch compromete operaciones heterogéneas como una unidad
    k_k1 = Kernel()
    k_k1.transition_batch([
        Transition("add_object", {"id": "ka", "type": "N"}),
        Transition("add_object", {"id": "kb", "type": "N"}),
        Transition("add_relation", {"id": "kr1", "source": "ka", "predicate": "p", "target": "kb"}),
    ])
    k1_ok = ("ka" in k_k1.state.objects and "kb" in k_k1.state.objects and "kr1" in k_k1.state.relations)
    suite_results.append((
        "K1. transition_batch compromete operaciones heterogéneas atómicamente", k1_ok,
        "add_object + add_object + add_relation aplicados como una sola unidad."
    ))

    # K2: si CUALQUIER paso del batch falla, NADA se compromete (rollback por identidad)
    k_k2 = Kernel()
    k_k2.transition(Transition("add_object", {"id": "kx", "type": "N"}))
    snapshot_k2 = k_k2.state
    k2_raised = False
    try:
        k_k2.transition_batch([
            Transition("add_object", {"id": "ky", "type": "N"}),
            Transition("add_relation", {"id": "kr_bad", "source": "kx", "predicate": "p", "target": "no_existe"}),
        ])
    except MissingReferenceError:
        k2_raised = True
    k2_ok = k2_raised and (k_k2.state is snapshot_k2) and ("ky" not in k_k2.state.objects)
    suite_results.append((
        "K2. transition_batch: un solo paso inválido rechaza TODO el lote", k2_ok,
        "'ky' se descarta aunque su propia operación era válida, porque el lote entero es la unidad atómica; state idéntico por identidad al previo."
    ))

    # K3: transition_batch generaliza batch_derive (mismo resultado alcanzable por ambas vías)
    k_k3a = Kernel()
    for o in ["p1", "p2"]:
        k_k3a.transition(Transition("add_object", {"id": o, "type": "N"}))
    k_k3a.transition(Transition("batch_derive", {"relations": [
        {"id": "d1", "source": "p1", "predicate": "step", "target": "p2", "origin": "derived", "rule_id": "R", "premises": ()}
    ]}))
    k_k3b = Kernel()
    for o in ["p1", "p2"]:
        k_k3b.transition(Transition("add_object", {"id": o, "type": "N"}))
    k_k3b.transition_batch([
        Transition("add_relation", {"id": "d1b", "source": "p1", "predicate": "step", "target": "p2", "origin": "derived", "rule_id": "R", "premises": ()})
    ])
    k3_ok = project_pi(k_k3a.state) == project_pi(k_k3b.state)
    suite_results.append((
        "K3. transition_batch generaliza batch_derive (mismo π alcanzable por ambas vías)", k3_ok,
        "batch_derive queda intacto para compatibilidad; transition_batch no lo reemplaza, produce el mismo hecho semántico por un camino más general."
    ))

    # K4: origin='proposed' se acepta y es distinguible
    k_k4 = Kernel()
    k_k4.transition(Transition("add_object", {"id": "ka4", "type": "N"}))
    k_k4.transition(Transition("add_object", {"id": "kb4", "type": "N"}))
    k_k4.transition(Transition("add_relation", {"id": "kp4", "source": "ka4", "predicate": "dice", "target": "kb4", "origin": "proposed"}))
    k4_ok = k_k4.state.relations["kp4"].origin == "proposed"
    suite_results.append((
        "K4. origin='proposed' se acepta como tercera categoría junto a asserted/derived", k4_ok,
        "Un hecho propuesto externamente puede existir en el estado y queda etiquetado como tal."
    ))

    # K5: promote_relation transforma proposed -> asserted; rechaza promover lo que no es proposed
    k5_promoted_ok = (k_k4.state.relations["kp4"].origin == "proposed")
    k_k4.transition(Transition("promote_relation", {"id": "kp4"}))
    k5_after_ok = (k_k4.state.relations["kp4"].origin == "asserted")
    k5_rejects_non_proposed = False
    try:
        k_k4.transition(Transition("promote_relation", {"id": "kp4"}))  # ya es asserted, no debe volver a promoverse
    except InvalidTransitionError:
        k5_rejects_non_proposed = True
    k5_ok = k5_promoted_ok and k5_after_ok and k5_rejects_non_proposed
    suite_results.append((
        "K5. promote_relation: proposed->asserted, y rechaza promover lo que no es proposed", k5_ok,
        "La promoción es la única vía formal de aceptar un hecho propuesto; promover algo que ya no es 'proposed' se rechaza explícitamente."
    ))

    # K6: EngineD NO usa hechos 'proposed' como premisa para derivar — hasta que se promueven
    k_k6 = Kernel()
    for o in ["ea", "eb", "ec"]:
        k_k6.transition(Transition("add_object", {"id": o, "type": "N"}))
    k_k6.transition(Transition("add_relation", {"id": "e_ab", "source": "ea", "predicate": "step", "target": "eb", "origin": "asserted"}))
    k_k6.transition(Transition("add_relation", {"id": "e_bc_proposed", "source": "eb", "predicate": "step", "target": "ec", "origin": "proposed"}))
    rule_k6 = Rule("R_K6", "T", (Pattern("step", "?X", "?Y"), Pattern("step", "?Y", "?Z")), Pattern("step", "?X", "?Z"))
    engine_k6 = EngineD(k_k6)
    n_before_promote = engine_k6.saturate([rule_k6])
    no_derivation_while_proposed = not any(r.predicate == "step" and r.source == "ea" and r.target == "ec" for r in k_k6.state.relations.values())
    k_k6.transition(Transition("promote_relation", {"id": "e_bc_proposed"}))
    n_after_promote = engine_k6.saturate([rule_k6])
    derivation_after_promote = any(r.predicate == "step" and r.source == "ea" and r.target == "ec" for r in k_k6.state.relations.values())
    k6_ok = (n_before_promote == 0) and no_derivation_while_proposed and (n_after_promote == 1) and derivation_after_promote
    suite_results.append((
        "K6. EngineD excluye origin='proposed' de sus premisas hasta que se promueve", k6_ok,
        "Con e_bc_proposed sin promover, saturate() no deriva ea->ec (0 derivados); tras promover, sí deriva exactamente eso — 'proponer' no otorga autoridad para generar más conocimiento por sí solo."
    ))

    # K7: extract_facts_from_text produce Transitions válidas, origin='proposed', end-to-end
    k_k7 = Kernel()
    texto_k7 = "El sol calienta la tierra. La tierra orbita el sol -> la luna orbita la tierra"
    propuestas_k7 = extract_facts_from_text(texto_k7, k_k7, predicate="implica")
    k7_transitions_valid = all(isinstance(t, Transition) for t in propuestas_k7)
    k_k7.transition_batch(propuestas_k7)
    proposed_relations_k7 = [r for r in k_k7.state.relations.values() if r.origin == "proposed"]
    k7_ok = k7_transitions_valid and len(propuestas_k7) > 0 and len(proposed_relations_k7) >= 1 and all(r.origin == "proposed" for r in proposed_relations_k7)
    suite_results.append((
        "K7. extract_facts_from_text: texto -> Transitions -> aplicadas como 'proposed'", k7_ok,
        f"{len(propuestas_k7)} Transition(s) propuestas desde texto libre, aplicadas atómicamente vía transition_batch, ninguna con origin distinto de 'proposed'."
    ))

    # ------------------------------------------------------------
    # RESULTADOS FINALES
    # ------------------------------------------------------------
    all_passed = all(res[1] for res in suite_results)
    return suite_results, all_passed


if __name__ == "__main__":
    import sys
    sys.modules['mf_min_definitivo'] = sys.modules['__main__']
    results, all_ok = run_mf_min_closure_suite()

    print("=" * 80)
    print("MF_MIN — VERSIÓN DEFINITIVA (fusión verificada) — BATERÍA DE CIERRE")
    print("=" * 80)

    passed_count = sum(1 for r in results if r[1])

    for name, passed, explanation in results:
        status = "PASS" if passed else "FAIL"
        print(f"[{status}] {name}")
        if not passed:
            print(f"       DETALLE: {explanation}")

    print("-" * 80)
    print(f"RESULTADO: {passed_count}/{len(results)} TESTS PASSED")
    print("-" * 80)

    if all_ok:
        print("MF_MIN STATUS: CONSOLIDATED REFERENCE KERNEL + EXTENSIONES DE INGENIERÍA")
        print("\n" + "=" * 80)
        print("ADENDA — COMPOSICIÓN ATÓMICA Y PROPUESTAS EXTERNAS (GRUPO K)")
        print("=" * 80)
        print("\nEn respuesta a una arquitectura externa propuesta (Transformer/Gate/")
        print("Scheduler/Compositor/MF-IR/bytecode), se evaluó cada pieza por separado")
        print("y se implementó solo lo que una necesidad concreta justificaba:")
        print("  - Kernel.transition_batch(): generaliza batch_derive a CUALQUIER")
        print("    secuencia de operaciones, comprometida como una sola unidad atómica.")
        print("    Sustituye la necesidad de una clase Compositor: concatenar las")
        print("    propuestas de varias fuentes y pasarlas aquí ES la composición.")
        print("  - Relation.origin admite 'proposed' como tercera categoría: un hecho")
        print("    propuesto externamente puede existir y ser chequeado por los axiomas,")
        print("    pero EngineD lo excluye de sus premisas hasta que se promueve")
        print("    explícitamente (promote_relation) — verificado en K6, no solo")
        print("    declarado: 0 derivados con el hecho sin promover, 1 tras promoverlo.")
        print("  - extract_facts_from_text(): primer proponente real (texto -> ")
        print("    List[Transition], sin aplicarlas). El parser interno es un sustituto")
        print("    explícito de una llamada a LLM (este entorno no tiene acceso de red")
        print("    a APIs de modelos); el contrato de salida es el mismo que tendría un")
        print("    extractor real, así que sustituirlo es cambiar una función, no")
        print("    rediseñar nada.")
        print("\nDeliberadamente NO implementado (sin una segunda necesidad real que lo")
        print("justifique todavía): Scheduler, grafo de dependencias, MF-IR/bytecode,")
        print("compilación JIT/SIMD/GPU, telemetría como framework separado.")
        print("=" * 80)
        print("\n" + "=" * 80)
        print("CRITERIO DE CONGELACIÓN DEFINITIVO — NÚCLEO FORMAL")
        print("=" * 80)
        print("\nEl núcleo MF_MIN = ⟨O, M, A, δ⟩ queda formalmente congelado.")
        print("\nSEIS INVARIANTES ESTRUCTURALES, CADA UNA CON PRUEBA DIRECTA:")
        print("  I1. Unicidad global de identificadores (A2, C3)")
        print("  I2. Integridad referencial de M sobre O, y de premises sobre M (A4, C7, C9)")
        print("  I3. No-contradicción de polaridad (B4, H7, H12)")
        print("  I4. Unicidad semántica de hechos (A7)")
        print("  I5. Consistencia axiomática, incluyendo __distinct__ independiente del")
        print("      orden textual del cuerpo (B5, B6, B8, F2, G3)")
        print("  I6. Validez numérica: booleanos/NaN/Inf/rango rechazados, y los propios")
        print("      límites de un axioma deben ser finitos (A5, A6)")
        print("\nLO QUE EL NÚCLEO DEJA EXPLÍCITAMENTE FUERA DE ALCANCE (por decisión):")
        print("  • Irreductibilidad matemática FUERTE de M, A y δ (solo se demuestra para")
        print("    O, de forma acotada — G6). G1-G5 son independencia OPERACIONAL.")
        print("  • Expansión del lenguaje axiomático (disyunción, cardinalidad, igualdad")
        print("    como primitiva, cuantificadores anidados).")
        print("  • Semántica de 'proof-relevance' (una justificación canónica por hecho,")
        print("    no múltiples pruebas alternativas).")
        print("\n" + "=" * 80)
        print("EXTENSIONES DE INGENIERÍA (lo que antes no existía; CAPA 4-7)")
        print("=" * 80)
        print("\nPERSISTENCIA (CAPA 4):")
        print("  • save_state()/load_state(): ciclo completo en JSON; Kernel(load_state(...))")
        print("    re-valida al reconstruir — un archivo corrupto se rechaza, no se acepta")
        print("    silenciosamente (I1, P3 en verificación adversarial).")
        print("  • save_rules()/load_rules(): las reglas de EngineD también se persisten,")
        print("    no solo los hechos ya derivados (I8).")
        print("  • Limitación conocida y no oculta: JSON no distingue tuple/list ni")
        print("    set/frozenset, y exige claves de objeto en string — el CONTENIDO")
        print("    sobrevive, el tipo exacto de contenedor puede cambiar (ver docstring")
        print("    de CAPA 4 y prueba P1/P2 en verificación adversarial).")
        print("\nRENDIMIENTO (CAPA 5) — medido antes y después, no solo afirmado:")
        print("  • EvaluatorA indexa relaciones por (predicate, polarity): una transición")
        print("    con axiomas cuyo predicado NO coincide con las relaciones existentes")
        print("    pasó de escanear todo el estado a O(1). Caso desfavorable (el axioma SÍ")
        print("    comparte predicado con todo) medido en escala lineal, no peor.")
        print("  • EngineD.infer_step ya no reescanea todas las relaciones por cada")
        print("    candidato derivado para preguntar '¿ya existe?' (ahora O(1) vía un solo")
        print("    project_pi() por llamada).")
        print("  • LÍMITE HONESTO QUE NINGÚN ÍNDICE ELIMINA: una regla de 2+ premisas que")
        print("    computa clausura transitiva completa sigue siendo intrínsecamente cara")
        print("    (medido: cadena de 45 nodos, 0.14s; de 200 nodos, 14.5s) porque la")
        print("    evaluación es 'ingenua' (reúne todo contra todo en cada ronda). La")
        print("    solución real -evaluación semi-ingenua- es un cambio algorítmico más")
        print("    profundo que queda fuera de esta sesión. saturate(max_rounds=,")
        print("    max_total_derived=) aborta con error claro en vez de consumir tiempo")
        print("    sin aviso — es una salvaguarda, no una eliminación del costo.")
        print("\nCONCURRENCIA (CAPA 6):")
        print("  • Kernel puro NO es seguro para hilos concurrentes: confirmado que puede")
        print("    perder actualizaciones bajo carga real (no solo en teoría).")
        print("  • ThreadSafeKernel serializa transition() con un RLock: verificado sin")
        print("    pérdidas en corridas repetidas bajo la misma carga concurrente.")
        print("  • Es exclusión mutua, no paralelismo de escritura — adecuado para uso por")
        print("    ráfagas, no para escritura sostenida de muy alta frecuencia.")
        print("\nCAPA DE USO (CAPA 7):")
        print("  • MFMin: fachada encadenable sobre Kernel+EngineD; no duplica lógica,")
        print("    arma los mismos Transition/payload y delega (verificado por equivalencia")
        print("    de estado contra las llamadas crudas, no solo por inspección).")
        print("  • Punto de partida, no diseño de interfaz definitivo: no asume CLI, API")
        print("    web, ni ningún consumidor específico todavía.")
        print("\nEsta suite demuestra el cierre operacional del contrato declarado y la")
        print("corrección medida de las extensiones de ingeniería.")
        print("NO demuestra completitud matemática universal, optimalidad del núcleo, ni")
        print("que el costo combinatorio de reglas de clausura transitiva esté resuelto.")
        print("\nLas nuevas capacidades cognitivas (memoria, aprendizaje, planificación,")
        print("agentes, temporalidad, probabilidad, etc.) se construirán SOBRE este")
        print("núcleo, no DENTRO de él, salvo contraejemplo real al contrato actual.")
        print("=" * 80)
    else:
        print("MF_MIN STATUS: FAILED")
    print("=" * 80)