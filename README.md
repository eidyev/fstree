# 📂 # fstree

`fstree` es una herramienta en Python para **exportar** la estructura de un directorio a un archivo `.txt` estilo `tree`, **reconstruir** directorios a partir de un archivo `.txt`, y **validar** los procesos de construcción o exportación.

---

## Requisitos

- Python 3.8+
- Compatible Windows y Linux

---

## Instalación

```bash
sudo install_fstree.py
```
---

## 📖 Uso

### Revisar la ayuda
```bash
 fstree --help
```

```
fstree --help

usage: fstree [MODE] [OPTION]... SOURCE DEST
  or: fstree [MODE] [OPTION]... -t DEST SOURCE...

Modos:
  dump    Exporta un directorio a un archivo .txt
  build   Reconstruye un directorio desde un archivo .txt
  test    Valida un proceso build o dump

positional arguments:
  {dump,build,test}         Modo de operación: dump, build o test
  entrada                   Archivo de entrada o directorio según el modo
  salida                    Archivo de salida o directorio según el modo

options:
  -h, --help                show this help message and exit
  
  -v, --verbose             Muestra acciones detalladas
  
  --overwrite               Sobrescribir archivos existentes (solo build)
  
  --with-content            Incluir contenido de archivos (solo dump)
  
  -d, --dirs-only           Listar solo directorios (omitirá archivos) en dump
  
  -L LEVEL, --level LEVEL   Limitar profundidad de directorios (solo dump)
 
  --exclude EXCLUDE     Lista separada por comas de nombres a excluir (ej: .git,node_modules,vendor)
 
  --exclude-file EXCLUDE_FILE
                        Archivo que contiene nombres de exclusión
  --test-mode {dump,build}
                        Indica qué proceso validar cuando se usa --mode test

```

### Reconstruir un directorio desde un archivo
```bash
 fstree build estructura.txt ./restaurado --verbose
```

### Exportar un directorio
```bash
 fstree dump ./mi_proyecto estructura.txt --verbose
```

### Reconstruir sobrescribiendo archivos existentes
```bash
 fstree build estructura.txt ./restaurado --overwrite --verbose
```

---

## 🗑️ Desinstalación

```bash
 sudo install_fstree.py --uninstall
```


---

## Ejemplo de archivo de estructura

Nota: los  directorios deben terminar el en caracter /


```
 app/
├── src/
│   ├── Application/
│   │   ├── Auth/
│   │   │   ├── Command/
│   │   │   └── CommandHandler/
│   │   ├── Notification/
│   │   │   └── CommandHandler/
│   │   ├── DeveloperPortal/
│   │   │   └── CommandHandler/
│   │   └── Analytics/
│   │       └── QueryHandler/
│   └── UI/
│       ├── Http/
│       │   ├── Controller/
│       │   │   ├── RegistrationController.php
│       │   │   ├── LoginController.php
│       │   │   ├── DashboardController.php
│       │   │   └── DeveloperController.php
│       │   └── API/
│       │       ├── UserController.php
│       │       ├── AuthController.php
│       │       └── DeveloperAPIController.php
│       └── Web/
│           ├── RegistrationWizard/
│           │   ├── step1.html.twig
│           │   ├── step2.html.twig
│           │   └── step3.html.twig
│           ├── Dashboard/
│           │   └── dashboard.html.twig
│           ├── DeveloperPortal/
│           │   └── developer_dashboard.html.twig
│           └── Shared/
│               ├── base.html.twig
│               └── theme.html.twig
├── translations/
│   ├── messages.en.yaml
│   └── messages.es.yaml
├── docker-compose.yml
├── Makefile   # Opcional: comandos de build, migrate, fixtures
└── README.md
```
