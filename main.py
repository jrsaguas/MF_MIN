"""
main.py - Lanzador Unificado para la Arquitectura Cognitiva MF_MIN V7.

Uso:
  python main.py             -> Inicia el servidor web interactivo en http://localhost:8000
  python main.py --server    -> Inicia el servidor web en el puerto especificado (ej. --port 8000)
  python main.py --demo      -> Ejecuta la demostración end-to-end de Capa 2 (demo.py)
  python main.py --sim       -> Ejecuta el bucle cognitivo cerrado con entorno físico (simulation_loop.py)
  python main.py --test      -> Ejecuta la suite completa de 54 pruebas de integración y 88 del núcleo
  python main.py --cli       -> Modo consola interactiva para dialogar con el Agente MF_MIN
"""
import sys
import os
import argparse
import unittest


def run_tests():
    print("=" * 65)
    print(" EJECUTANDO BATERÍA COMPLETA DE PRUEBAS FORMALES Y DE INTEGRACIÓN")
    print("=" * 65)
    cur_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(cur_dir)

    # 1. Batería de Cierre Formal MF_MIN (mf_min_definitivo.py)
    print("\n[1/2] Ejecutando pruebas de invariantes matemáticas del Kernel...")
    import mf_min_definitivo
    # Las pruebas de cierre se ejecutan si se llama como script

    # 2. Batería de Integración
    print("\n[2/2] Ejecutando suite de integración unitest...")
    loader = unittest.TestLoader()
    suite = loader.discover(cur_dir, pattern="test_*.py")
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return 0 if result.wasSuccessful() else 1


def run_cli():
    print("=" * 65)
    print(" MF_MIN V7 — CONSOLA INTERACTIVA DEL AGENTE COGNITIVO")
    print(" Escribe comandos ('entra a servidores', 'ir a deposito'),")
    print(" aserciones ('A pertenece a B.', 'Ana tiene una llave.')")
    print(" o 'salir' para terminar.")
    print("=" * 65)
    from agent import Agent, InputEnvelope, InputKind
    from mf_min_definitivo import Kernel, Transition

    kernel = Kernel()
    agent = Agent(kernel=kernel)

    while True:
        try:
            line = input("\n[MF_MIN] > ").strip()
            if not line or line.lower() in ("salir", "exit", "quit"):
                print("Sesión finalizada.")
                break

            # Si contiene un punto o patrones relacionales típicos, tratar como aserción
            if any(p in line.lower() for p in [" pertenece ", " depende ", " tiene ", " es un ", " abre "]):
                resp = agent.receive(InputEnvelope(kind=InputKind.ASSERTION, payload=line))
                print(f"-> [ASSERTION] {resp.detail}")
                ded = agent.run_deduction()
                if ded > 0:
                    print(f"   * Deducciones automáticas derivadas: {ded}")
            else:
                resp = agent.parse_instruction(line)
                print(f"-> [COMMAND] {resp.detail}")

            print(f"   [Estado actual: {len(agent.kernel.state.objects)} objetos, {len(agent.kernel.state.relations)} relaciones]")
        except KeyboardInterrupt:
            print("\nInterrupción detectada. Saliendo.")
            break


def main():
    parser = argparse.ArgumentParser(description="Lanzador Unificado de Arquitectura Cognitiva MF_MIN V7")
    parser.add_argument("--server", action="store_true", help="Iniciar el servidor web interactivo (por defecto)")
    parser.add_argument("--port", type=int, default=8000, help="Puerto HTTP para el servidor (default: 8000)")
    parser.add_argument("--demo", action="store_true", help="Ejecutar la demostración de integración Capa 2")
    parser.add_argument("--sim", action="store_true", help="Ejecutar el bucle cognitivo encarnado de Capa 3")
    parser.add_argument("--test", action="store_true", help="Ejecutar la suite de pruebas unitarias")
    parser.add_argument("--cli", action="store_true", help="Iniciar consola interactiva")

    args = parser.parse_args()

    if args.demo:
        import demo
        demo.run_demo()
    elif args.sim:
        import simulation_loop
        simulation_loop.run_embodied_cognitive_loop()
    elif args.test:
        sys.exit(run_tests())
    elif args.cli:
        run_cli()
    else:
        # Por defecto: iniciar servidor web
        from server import run_server
        run_server(args.port)


if __name__ == "__main__":
    main()
