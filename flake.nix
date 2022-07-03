{
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixpkgs-unstable";
    utils.url = "github:gytis-ivaskevicius/flake-utils-plus";
  };

  outputs = { self, nixpkgs, utils } @ inputs:
    utils.lib.mkFlake {
      inherit self inputs;

      outputsBuilder = channels:
        let pkgs = channels.nixpkgs; in
        with pkgs;
        rec {
          devShells = rec {
            default = mindustry-svg-renderer;
            mindustry-svg-renderer = (poetry2nix.mkPoetryEnv { projectDir = ./.; }).env;
          };

          packages = (self.overlays.default pkgs pkgs) // {
            default = packages.mindustry-svg-renderer;
          };
        };

      overlays = rec {
        default = mindustry-svg-renderer;
        mindustry-svg-renderer = final: _prev: {
          mindustry-svg-renderer = final.poetry2nix.mkPoetryApplication { projectDir = ./.; };
        };
      };
    };
}
