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
            default = mindustry-sprite-renderer;
            mindustry-sprite-renderer = (poetry2nix.mkPoetryEnv { projectDir = ./.; }).env;
          };

          packages = (self.overlays.default pkgs pkgs) // {
            default = packages.mindustry-sprite-renderer;
          };
        };

      overlays = rec {
        default = mindustry-sprite-renderer;
        mindustry-sprite-renderer = final: _prev: {
          mindustry-sprite-renderer = final.poetry2nix.mkPoetryApplication { projectDir = ./.; };
        };
      };
    };
}
