{
  description = "jyyslide-util nix flake configuration";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = {
    self,
    nixpkgs,
    flake-utils
  }: flake-utils.lib.eachDefaultSystem (system: let
    pkgs = nixpkgs.legacyPackages.${system};

    python = pkgs.python313;

    projectName = "jyyslide-util";

    pythonDevPkgs = ps: with ps; [
      hatchling
      hatch-vcs
    ];

    pythonEnv = python.withPackages (ps: 
      (pythonDevPkgs ps)
    );

    myApp = pkgs.python3Packages.buildPythonApplication {
      pname = projectName;

      version = let
        rev = self.shortRev or self.dirtyRev or "dirty";
      in "0.1.0+${rev}";

      format = "pyproject";

      src = pkgs.lib.cleanSourceWith {
        src = ./.;
        filter = path: type: (
          (pkgs.lib.cleanSourceFilter path type) &&
          !(pkgs.lib.hasSuffix ".egg-info" path) &&
          !(pkgs.lib.hasInfix "/.git" path) &&
          !(pkgs.lib.hasSuffix "/__pycache__" path) &&
          !(pkgs.lib.hasSuffix ".nix" path)
        );
      };

      propagatedBuildInputs = with pkgs.python3Packages; [
        jinja2
        pyquery
        pyyaml
        markdown
        requests
      ];
      nativeBuildInputs = with pkgs.python3Packages; [
        hatchling
        hatch-vcs
        setuptools-scm
      ];
    };
  in {
    # === development shell ===
    devShells.default = pkgs.mkShell {
      name = "${projectName}-dev";
      packages = [
        pythonEnv
        pkgs.git
      ];

      shellHook = ''
        export REPO_ROOT=$(git rev-parse --show-toplevel)
        echo "Development shell for ${projectName}."
        echo "  run 'hatch version' to see the current version."
        echo "  run 'hatch run pytest' to run the test suite."
        echo "  run 'hatch fmt' to format the code."
      '';
    };

    # === nix build ===
    packages.default = myApp;
    packages.wheel = myApp;

    # === nix run ===
    apps.default = flake-utils.lib.mkApp {
      drv = myApp;
      program = "${myApp}/bin/jyyslide-util";
    };

    # === check & format ===
    checks.default = myApp;
    formatter = pkgs.nixpkgs-fmt;
  });
}
