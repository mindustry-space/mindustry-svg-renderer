{
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixpkgs-unstable";
    utils.url = "github:gytis-ivaskevicius/flake-utils-plus";
  };

  outputs = { self, nixpkgs, utils } @ inputs:
    let
      overrides = pkgs:
        pkgs.poetry2nix.overrides.withDefaults
          (self: super: {
            evdev = super.evdev.overridePythonAttrs (old: {
              preConfigure = ''
                substituteInPlace setup.py --replace /usr/include/linux ${pkgs.linuxHeaders}/include/linux
              '';
            });

            pynput = super.pynput.overridePythonAttrs (old: {
              nativeBuildInputs = (old.nativeBuildInputs or [ ])
                ++ [ self.sphinx ];

              propagatedBuildInputs = (old.propagatedBuildInputs or [ ])
                ++ [ self.setuptools-lint ];
            });
          });
    in

    utils.lib.mkFlake {
      inherit self inputs;

      outputsBuilder = channels:
        let pkgs = channels.nixpkgs; in
        with pkgs;
        rec {
          devShells = rec {
            default = mindustry-svg-renderer;
            mindustry-svg-renderer = (poetry2nix.mkPoetryEnv {
              overrides = overrides pkgs;
              projectDir = ./.;
            }).env;
          };

          packages = (self.overlays.default pkgs pkgs) // {
            default = packages.mindustry-svg-renderer;
          };
        };

      overlays = rec {
        default = mindustry-svg-renderer;
        mindustry-svg-renderer = final: _prev: {
          mindustry-svg-renderer = final.poetry2nix.mkPoetryApplication {
            overrides = overrides final;
            projectDir = ./.;
          };
        };
      };
    };
}
