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
            mindustry-svg-renderer = mkShell {
              packages = [
                (python3.withPackages (ps: with ps; [
                  pillow
                  pynput
                  rich
                ]))
              ];
            };
          };
        };
    };

  # TODO: evdev fails to build
}
