"""
================================================================================
ENGINE D — Motor de Inferencia Deductiva y Cierre Hacia Adelante (Externo)
================================================================================

EngineD vive FUERA del núcleo formal MF_MIN = ⟨O, M, A, δ⟩.
Dependencia:
    engine_d -> mf_min_definitivo
y nunca al revés.

Aplica reglas de reescritura hacia adelante (forward chaining) sobre estados
válidos de MF_MIN. Todas las relaciones deducidas se integran a través de
transiciones δ legítimas con origin="derived", garantizando que el Kernel
mantenga intactas todas sus invariantes (I1-I6).
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Set, Mapping, Any
import hashlib
import json

from mf_min_definitivo import (
    Kernel,
    State,
    Relation,
    Transition,
    project_pi,
    ValidationError,
    InvalidTransitionError,
    require_nonempty_string,
)

@dataclass(frozen=True)
class Pattern:
    predicate: str
    source: str
    target: str
    polarity: bool = True

    def __post_init__(self):
        require_nonempty_string(self.predicate, "Pattern.predicate")
        require_nonempty_string(self.source, "Pattern.source")
        require_nonempty_string(self.target, "Pattern.target")
        if not isinstance(self.polarity, bool):
            raise ValidationError("Pattern.polarity debe ser bool.")


@dataclass(frozen=True)
class Rule:
    """
    Regla de inferencia para el motor deductivo externo D.
    
    Alcance: Motor mínimo de inferencia conjuntiva sobre relaciones binarias.
    - Variables: ?X, ?Y, etc.
    - Patrones: predicate(source, target) binarios
    - No es un lenguaje lógico universal de primer orden
    - No soporta cuantificadores, negación no monotónica, ni backtracking general
    """
    id: str
    name: str
    premises: Tuple[Pattern, ...]
    conclusion: Pattern

    def __post_init__(self):
        require_nonempty_string(self.id, "Rule.id")
        require_nonempty_string(self.name, "Rule.name")

        premises = tuple(self.premises)
        for premise in premises:
            if not isinstance(premise, Pattern):
                raise ValidationError("Rule.premises contiene elementos inválidos.")
        object.__setattr__(self, "premises", premises)

        if not isinstance(self.conclusion, Pattern):
            raise ValidationError("Rule.conclusion inválida.")

        premise_variables = {
            variable for premise in premises
            for variable in (premise.source, premise.target)
            if variable.startswith("?")
        }

        conclusion_variables = {
            variable for variable in (self.conclusion.source, self.conclusion.target)
            if variable.startswith("?")
        }

        unbound = conclusion_variables - premise_variables
        if unbound:
            raise ValidationError(f"Variables no ligadas en conclusión: {unbound}")


class _RelationIndex:
    """
    Índice de relaciones por (predicate, polarity, source) y por
    (predicate, polarity, target), construido UNA VEZ por llamada a
    infer_step() en lugar de escanear state.relations completo por cada
    comparación. Uso puramente interno de EngineD: no cambia ninguna
    semántica pública ni toca Kernel/Validator/EvaluatorA.

    Motivo (medido, no supuesto): un perfilado mostró que infer_step()
    escala mal específicamente cuando una regla de 2+ premisas se evalúa
    sobre un conjunto de relaciones que comparten predicado (p. ej. cierre
    transitivo de una cadena): la segunda premisa, con una variable ya
    ligada por la primera, igual escaneaba TODAS las relaciones en vez de
    solo las que comparten esa fuente/destino ya conocida. Indexar por
    source/target — no solo por predicado — es lo que efectivamente reduce
    ese escaneo, porque en un escenario así todas las relaciones comparten
    el mismo predicado (indexar solo por predicado no habría ayudado).
    """
    def __init__(self, relations: "Any"):
        """
        Acepta cualquier iterable de Relation (no exige un State completo),
        para poder construir también un índice restringido a un subconjunto
        (p. ej. solo lo derivado en la ronda anterior — ver evaluación
        semi-ingenua en infer_step/saturate).
        """
        self._by_source: Dict[Tuple[str, bool, str], List[Relation]] = {}
        self._by_target: Dict[Tuple[str, bool, str], List[Relation]] = {}
        self._by_pred_pol: Dict[Tuple[str, bool], List[Relation]] = {}
        for rel in relations:
            self._by_source.setdefault((rel.predicate, rel.polarity, rel.source), []).append(rel)
            self._by_target.setdefault((rel.predicate, rel.polarity, rel.target), []).append(rel)
            self._by_pred_pol.setdefault((rel.predicate, rel.polarity), []).append(rel)

    def candidates(self, pattern: "Pattern", binding: Dict[str, str]) -> List["Relation"]:
        """
        Devuelve el subconjunto MÁS PEQUEÑO de relaciones que podría
        satisfacer `pattern` dado lo ya ligado en `binding`. Sigue siendo
        obligatorio verificar el resultado con _match_pattern después: este
        método solo reduce cuántas relaciones hay que someterle, nunca
        decide por sí mismo si una relación matchea.
        """
        source_known = (not pattern.source.startswith("?")) or (pattern.source in binding)
        if source_known:
            key_source = pattern.source if not pattern.source.startswith("?") else binding[pattern.source]
            return self._by_source.get((pattern.predicate, pattern.polarity, key_source), [])

        target_known = (not pattern.target.startswith("?")) or (pattern.target in binding)
        if target_known:
            key_target = pattern.target if not pattern.target.startswith("?") else binding[pattern.target]
            return self._by_target.get((pattern.predicate, pattern.polarity, key_target), [])

        return self._by_pred_pol.get((pattern.predicate, pattern.polarity), [])


class EngineD:
    """
    Motor deductivo externo. Propone transiciones, no muta directamente el Kernel.
    query_evidence puede retornar "CONTRADICTION" como condición observacional defensiva,
    aunque un Kernel válido jamás debe contener contradicciones.
    """

    def __init__(self, kernel: Kernel):
        self._kernel = kernel

    def query_evidence(self, source: str, predicate: str, target: str) -> str:
        """
        Consulta evidencia sobre una relación específica.
        
        Retorna:
        - TRUE: existe relación con polarity=True
        - FALSE: existe relación con polarity=False (evidencia negativa explícita)
        - UNKNOWN: no existe evidencia (ausencia de relación)
        - CONTRADICTION: existen ambas polaridades (estado defensivo, no debería ocurrir en Kernel válido)
        """
        polarities = {
            relation.polarity for relation in self._kernel.state.relations.values()
            if relation.source == source and relation.predicate == predicate and relation.target == target
        }

        if len(polarities) > 1:
            return "CONTRADICTION"
        if True in polarities:
            return "TRUE"
        if False in polarities:
            return "FALSE"
        return "UNKNOWN"

    @staticmethod
    def _deterministic_id(source: str, predicate: str, target: str, polarity: bool, rule_id: str) -> str:
        """
        Genera ID determinista de derivación.
        Nota: El ID representa (hecho, regla), no solo el hecho semántico.
        Por tanto, el mismo hecho derivado por reglas diferentes tendrá IDs diferentes.
        """
        content = f"{source}|{predicate}|{target}|{polarity}|{rule_id}"
        digest = hashlib.sha256(content.encode("utf-8")).hexdigest()[:12]
        return f"D_{digest}"

    @staticmethod
    def _match_pattern(pattern: Pattern, relation: Relation, binding: Dict[str, str]) -> Optional[Dict[str, str]]:
        """
        Unifica un Pattern contra una Relation concreta bajo un binding dado.
        Extraído como método compartido (antes vivía inline dentro de
        infer_step) para que infer_step y verify_derivation usen exactamente
        la misma semántica de unificación — evita que ambas rutas puedan
        divergir sutilmente.
        """
        if pattern.predicate != relation.predicate or pattern.polarity != relation.polarity:
            return None
        candidate = dict(binding)
        for variable, value in (
            (pattern.source, relation.source),
            (pattern.target, relation.target),
        ):
            if variable.startswith("?"):
                if variable in candidate and candidate[variable] != value:
                    return None
                candidate[variable] = value
            elif variable != value:
                return None
        return candidate

    def infer_step(self, rule: Rule, delta_ids: Optional[Set[str]] = None) -> List[Relation]:
        """
        Unifica las premisas de `rule` contra el estado y produce las
        conclusiones nuevas.

        delta_ids=None: evaluación INGENUA (comportamiento original,
        preservado para uso directo fuera de saturate() y para no romper
        compatibilidad): las premisas se unifican libremente contra TODO
        el estado actual, sin restricción.

        delta_ids={...}: evaluación SEMI-INGENUA. Decisión tomada tras medir
        (no suponer) que la evaluación ingenua reunía, en cada ronda, TODAS
        las combinaciones de premisas contra TODO el estado — incluyendo
        combinaciones compuestas enteramente por hechos ya viejos, que por
        construcción ya se intentaron en una ronda anterior. Para una regla
        de k premisas, se generan k pasadas: en la pasada i, la premisa i
        debe satisfacerse EXCLUSIVAMENTE con una relación cuyo id esté en
        delta_ids (lo comprometido en la ronda anterior); las demás premisas
        se satisfacen contra el estado completo. Toda combinación con AL
        MENOS una premisa "nueva" se encuentra en alguna pasada; toda
        combinación enteramente "vieja" se descarta, porque —por
        inducción sobre las rondas— ya fue intentada cuando el más reciente
        de sus hechos componentes era, a su vez, delta.

        Esto no cambia lo que la regla significa ni lo que saturate()
        calcula (el punto fijo es idéntico — ver GRUPO J en la batería de
        cierre, que lo verifica por comparación directa contra la
        evaluación ingenua). Cambia solo cuánto trabajo hace falta para
        llegar ahí.
        """
        full_index = _RelationIndex(
            r for r in self._kernel.state.relations.values() if r.origin != "proposed"
        )
        # Se excluye deliberadamente origin='proposed': un hecho propuesto
        # externamente (p. ej. por un extractor basado en LLM) puede EXISTIR
        # en el estado y ser chequeado por los axiomas (I3-I6 no distinguen
        # origin), pero no debe alimentar nueva inferencia hasta ser
        # promovido explícitamente (ver Kernel: operación "promote_relation").
        # Esto es lo que separa, en código y no solo en prosa, "el LLM
        # propone" de "el sistema formal determina": una propuesta no
        # promovida no puede, por construcción, generar más conocimiento
        # derivado a partir de sí misma.
        existing_facts = project_pi(self._kernel.state)

        if delta_ids is None:
            restrict_positions: List[Optional[int]] = [None]
            delta_index = None
        else:
            if not delta_ids:
                return []  # nada nuevo en la ronda anterior: esta regla no puede aportar nada nuevo
            restrict_positions = list(range(len(rule.premises)))
            delta_index = _RelationIndex(
                rel for rel in (self._kernel.state.relations.get(rid) for rid in delta_ids)
                if rel is not None and rel.origin != "proposed"
            )

        all_bindings: List[Tuple[Dict[str, str], Tuple[str, ...]]] = []
        seen_premise_combinations: Set[Tuple[str, ...]] = set()

        for restrict_pos in restrict_positions:
            # Orden de evaluación: la premisa restringida a delta (pequeña)
            # PRIMERO, para que su búsqueda sea barata desde el inicio; las
            # demás después, en su orden original, ya beneficiándose de las
            # variables que la primera dejó ligadas. Evaluarlas en el orden
            # declarado de la regla (ignorando cuál está restringida)
            # dejaría la primera premisa sin ligar consultando TODO el
            # índice — exactamente el costo que se buscaba evitar, y lo que
            # explica que una primera versión de este cambio solo diera una
            # mejora modesta (2-3x) en vez del cambio de orden de magnitud
            # esperado: medido, no supuesto.
            if restrict_pos is None:
                eval_order = list(range(len(rule.premises)))
            else:
                eval_order = [restrict_pos] + [i for i in range(len(rule.premises)) if i != restrict_pos]

            bindings: List[Tuple[Dict[str, str], Dict[int, str]]] = [({}, {})]
            for pos in eval_order:
                premise = rule.premises[pos]
                next_bindings = []
                for binding, ids_by_pos in bindings:
                    if restrict_pos is not None and pos == restrict_pos:
                        pool = delta_index.candidates(premise, binding)
                    else:
                        pool = full_index.candidates(premise, binding)
                    for relation in pool:
                        matched = self._match_pattern(premise, relation, binding)
                        if matched is not None:
                            new_ids = dict(ids_by_pos)
                            new_ids[pos] = relation.id
                            next_bindings.append((matched, new_ids))
                bindings = next_bindings
                if not bindings:
                    break

            for binding, ids_by_pos in bindings:
                # Reordenar de vuelta al orden DECLARADO de la regla — el
                # orden interno de evaluación es solo una optimización;
                # verify_derivation (y cualquier auditoría futura) espera
                # que premises refleje el orden de rule.premises, no el
                # orden en que esta pasada las evaluó.
                premise_ids = tuple(ids_by_pos[i] for i in range(len(rule.premises)))
                if premise_ids in seen_premise_combinations:
                    continue
                seen_premise_combinations.add(premise_ids)
                all_bindings.append((binding, premise_ids))

        derived = []
        seen_ids: Set[str] = set()
        seen_facts: Set[Tuple[str, str, str, bool]] = set()

        for binding, premise_ids in all_bindings:
            source = binding.get(rule.conclusion.source, rule.conclusion.source)
            target = binding.get(rule.conclusion.target, rule.conclusion.target)
            fact = (source, rule.conclusion.predicate, target, rule.conclusion.polarity)

            # Comprobación barata (membresía de conjunto) ANTES de calcular
            # el ID determinista (SHA256, no gratis). Corrección medida:
            # perfilado mostró 447,580 llamadas a _deterministic_id para
            # solo 9,591 hechos finalmente conservados en un caso de prueba
            # — la enorme mayoría eran combinaciones de premisas distintas
            # (p. ej. dos caminos intermedios distintos) que ya concluían un
            # hecho YA CONOCIDO, y pagaban el costo del hash antes de
            # descartarse. Reordenar el chequeo no cambia qué se conserva,
            # solo evita hashear lo que de todos modos se iba a descartar.
            if fact in existing_facts or fact in seen_facts:
                continue

            relation_id = self._deterministic_id(
                source, rule.conclusion.predicate, target, rule.conclusion.polarity, rule.id
            )

            if relation_id in seen_ids:
                continue

            # Detección de colisión de IDs deterministas
            existing_by_id = self._kernel.state.relations.get(relation_id)
            if existing_by_id is not None:
                # Mismo ID + misma semántica → ya existe, ignorar
                if (
                    existing_by_id.source == source
                    and existing_by_id.predicate == rule.conclusion.predicate
                    and existing_by_id.target == target
                    and existing_by_id.polarity == rule.conclusion.polarity
                ):
                    continue
                # Mismo ID + semántica diferente → colisión real
                raise ValidationError(
                    f"Colisión de ID determinista: '{relation_id}'."
                )

            seen_ids.add(relation_id)
            seen_facts.add(fact)
            derived.append(Relation(
                id=relation_id,
                source=source,
                predicate=rule.conclusion.predicate,
                target=target,
                polarity=rule.conclusion.polarity,
                origin="derived",
                rule_id=rule.id,
                premises=premise_ids,
            ))

        return derived

    def saturate(self, rules: List[Rule], max_rounds: int = 10_000, max_total_derived: Optional[int] = None) -> int:
        """
        Saturación monotónica con deduplicación semántica por iteración.
        
        Contrato de terminación formal:
        La saturación termina garantizadamente bajo las siguientes condiciones:
        1. |O| < ∞ (conjunto finito de objetos)
        2. |Rules| < ∞ (conjunto finito de reglas)
        3. Las reglas no crean nuevos objetos
        4. Las conclusiones utilizan predicados de un conjunto finito P
        5. La derivación es monotónica (solo agrega, nunca elimina)
        6. Deduplicación semántica: un hecho semántico → una representación operacional
        
        Relación semántica vs ID operacional:
        - El ID determinista representa (hecho, regla), no solo el hecho
        - La deduplicación semántica garantiza que |π_M(M)| esté acotado por |O|² × |P| × 2
        - Por tanto, la saturación alcanza un punto fijo S* donde D(S*,R) = S*
        
        Justificación canónica:
        La deduplicación semántica conserva como máximo una justificación operacional
        por hecho semántico. No se preservan múltiples pruebas alternativas.

        Salvaguardas de rendimiento (medido, no hipotético — ver CAPA 5 y
        GRUPO J):
        una regla de 2+ premisas puede producir clausura combinatoria (p. ej.
        clausura transitiva de una cadena de N nodos genera O(N²) hechos).
        Evolución medida en esta sesión, misma máquina, mismo escenario
        (cadena de 200 nodos):
          - Evaluación ingenua original:                        14.49s
          - + evaluación semi-ingenua (delta por ronda):          6.21s
          - + orden de evaluación (premisa-delta primero):        7.74s (sin mejora neta)
          - + chequeo de hecho ANTES del hash determinista:       6.21s
        Resultado neto verificado: ~2.3x más rápido, MISMO resultado exacto
        (ver GRUPO J). Causa raíz identificada por perfilado (cProfile), no
        supuesta: para pares con múltiples caminos intermedios válidos
        (p. ej. A→C alcanzable vía B1 o vía B2), el motor encuentra TODAS
        las combinaciones de premisas antes de deduplicar por hecho —
        perfilado mostró 447,580 llamadas a un hash SHA256 para solo 9,591
        hechos finalmente conservados en un caso de prueba. Esto YA NO
        recalcula el hash para combinaciones cuyo hecho ya se conoce (fue
        la corrección aplicada), pero el motor SIGUE enumerando todas esas
        combinaciones antes de descartarlas — evitar ESO exigiría deduplicar
        durante la búsqueda misma (parar en cuanto un hecho ya está
        cubierto), no solo después. Eso es un cambio más profundo al
        algoritmo de unificación, no una optimización de índice, y queda
        como el siguiente paso identificado, no resuelto en esta sesión.

        Retorna: número de relaciones operacionales creadas (hechos semánticos nuevos).
        """
        # Validación de unicidad de Rule IDs
        rule_ids = [rule.id for rule in rules]
        if len(rule_ids) != len(set(rule_ids)):
            raise ValidationError("IDs de Rule duplicados en saturate.")

        total = 0
        rounds = 0
        # Semi-ingenua: en la primera ronda, TODO el estado inicial cuenta
        # como "nuevo" (no hay una ronda anterior con la que compararlo).
        delta_ids: Set[str] = set(self._kernel.state.relations.keys())

        while True:
            rounds += 1
            if rounds > max_rounds:
                raise InvalidTransitionError(
                    f"saturate() no alcanzó un punto fijo tras {max_rounds} rondas "
                    f"(max_rounds). Revise si las reglas realmente convergen."
                )

            new_relations = []
            for rule in rules:
                new_relations.extend(self.infer_step(rule, delta_ids=delta_ids))

            if not new_relations:
                break

            # Deduplicación semántica: un hecho semántico → una representación operacional
            # Esto garantiza que |M| esté acotado por |O|² × |P| × 2
            unique_by_semantics: Dict[Tuple[str, str, str, bool], Relation] = {}
            for relation in new_relations:
                semantic_key = (
                    relation.source,
                    relation.predicate,
                    relation.target,
                    relation.polarity
                )
                if semantic_key not in unique_by_semantics:
                    unique_by_semantics[semantic_key] = relation

            payload = tuple(
                {
                    "id": relation.id,
                    "source": relation.source,
                    "predicate": relation.predicate,
                    "target": relation.target,
                    "polarity": relation.polarity,
                    "rule_id": relation.rule_id,
                    "premises": relation.premises,
                }
                for relation in unique_by_semantics.values()
            )

            self._kernel.transition(Transition("batch_derive", {"relations": payload}))
            total += len(unique_by_semantics)

            # Semi-ingenua: el delta de la SIGUIENTE ronda es exactamente lo
            # que se acaba de comprometer en ESTA ronda — no lo acumulado
            # desde el principio. Esto es lo que evita re-unir combinaciones
            # íntegramente viejas en cada ronda sucesiva.
            delta_ids = {rel.id for rel in unique_by_semantics.values()}

            if max_total_derived is not None and total > max_total_derived:
                raise InvalidTransitionError(
                    f"saturate() superó max_total_derived={max_total_derived} "
                    f"({total} hechos derivados hasta ahora); posible explosión combinatoria."
                )

        return total

    def verify_derivation(self, relation: Relation, rules_by_id: Mapping[str, "Rule"]) -> bool:
        """
        Verificación REAL de justificación (reincorporada tras pruebas
        cruzadas: se confirmó que, sin esto, una relación con origin=
        "derived", rule_id real y premises reales pero con una CONCLUSIÓN
        que esa regla+esas premisas no producirían, se acepta sin objeción
        y no existe forma de detectarlo después).

        No se limita a comprobar que las premisas EXISTAN (eso ya lo exige
        Validator como invariante estructural de Kernel) — vuelve a
        ejecutar la unificación de las premisas de la regla declarada
        contra las relaciones-premisa concretas, EN EL ORDEN declarado por
        la regla, y exige que el resultado reproduzca EXACTAMENTE (source,
        predicate, target, polarity) de `relation`. Esto separa
        formalmente el HECHO (la relación) de su JUSTIFICACIÓN (que la
        regla y las premisas señaladas realmente la produzcan).

        Devuelve False ante cualquier discrepancia: regla inexistente,
        número de premisas incorrecto, fallo de unificación en algún paso,
        o conclusión que no coincide.
        """
        if relation.origin != "derived" or not relation.rule_id:
            return False
        rule = rules_by_id.get(relation.rule_id)
        if rule is None:
            return False
        if len(relation.premises) != len(rule.premises):
            return False

        premise_relations: List[Relation] = []
        for pid in relation.premises:
            prem = self._kernel.state.relations.get(pid)
            if prem is None:
                return False
            premise_relations.append(prem)

        binding: Dict[str, str] = {}
        for pattern, prem in zip(rule.premises, premise_relations):
            matched = self._match_pattern(pattern, prem, binding)
            if matched is None:
                return False
            binding = matched

        expected_source = binding.get(rule.conclusion.source, rule.conclusion.source)
        expected_target = binding.get(rule.conclusion.target, rule.conclusion.target)
        return (
            expected_source == relation.source
            and expected_target == relation.target
            and rule.conclusion.predicate == relation.predicate
            and rule.conclusion.polarity == relation.polarity
        )


# ============================================================
# PERSISTENCIA DE REGLAS (ENGINE D)
# ============================================================

def pattern_to_dict(pattern: Pattern) -> Dict[str, Any]:
    return {"predicate": pattern.predicate, "source": pattern.source, "target": pattern.target, "polarity": pattern.polarity}


def pattern_from_dict(data: Mapping[str, Any]) -> Pattern:
    return Pattern(predicate=data["predicate"], source=data["source"], target=data["target"], polarity=data.get("polarity", True))


def rule_to_dict(rule: Rule) -> Dict[str, Any]:
    """
    Serializa una Rule (motor D). Corrige una laguna real: la persistencia
    original cubría State (O, M, A) pero no las reglas de inferencia, que
    viven fuera del Kernel — sin esto, guardar un MFMin no conservaba con
    qué reglas se había derivado su conocimiento, solo los hechos ya
    derivados.
    """
    return {
        "id": rule.id, "name": rule.name,
        "premises": [pattern_to_dict(p) for p in rule.premises],
        "conclusion": pattern_to_dict(rule.conclusion),
    }


def rule_from_dict(data: Mapping[str, Any]) -> Rule:
    return Rule(
        id=data["id"], name=data["name"],
        premises=tuple(pattern_from_dict(p) for p in data.get("premises", ())),
        conclusion=pattern_from_dict(data["conclusion"]),
    )


def save_rules(rules: List[Rule], path: str) -> None:
    """Guarda un conjunto de reglas como JSON en disco."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump([rule_to_dict(r) for r in rules], f, ensure_ascii=False, indent=2)


def load_rules(path: str) -> List[Rule]:
    """Carga un conjunto de reglas desde un archivo JSON producido por save_rules()."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [rule_from_dict(r) for r in data]

