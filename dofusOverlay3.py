import traceback
from main import main

try:
    # ton code principal
    main()
except Exception:
    print("Une erreur est survenue :")
    traceback.print_exc()
    input("Appuyez sur Entrée pour quitter...")
