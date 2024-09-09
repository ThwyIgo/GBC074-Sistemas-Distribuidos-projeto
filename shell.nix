{ pkgs ? import <nixpkgs> {} }:

let vscode' = (pkgs.vscode-with-extensions.override {
#      vscode = pkgs.vscodium;
      vscodeExtensions = with pkgs.vscode-extensions; [
        ms-python.python
        ms-python.vscode-pylance
        ms-python.debugpy
        ms-toolsai.jupyter
        tuttieee.emacs-mcx
        dracula-theme.theme-dracula
        ms-ceintl.vscode-language-pack-pt-br
      ];
    });
in
(pkgs.buildFHSEnv {
  name = "FHS";
  targetPkgs = pkgs: with pkgs; [
    (python3.withPackages (pyPkgs: with pyPkgs; [
      paho-mqtt
    ]))
    mosquitto
    vscode'
  ];
}
).env
