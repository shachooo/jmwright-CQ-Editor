name: build-PIP-TAR

on:
  schedule:
    - cron: '0 0 * * 1'
  workflow_dispatch:
    inputs:
      type:
        description: 'Whether to build a single file (onefile) or directory (dir) dist'
        required: true
        default: 'dir'

jobs:
  build-windows:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4

      - uses: mamba-org/setup-micromamba@v1
        with:
          environment-name: test
          environment-file: environment.yml
          init-shell: >-
            bash

      - name: pip install packages
        shell: bash --login -e {0}
        run: |
          micromamba info
          # 環境破壊を防ぐため vtk は外し、純粋に足りない runtype だけを追加します
          pip install runtype
          pip install git+https://github.com/jdegenstein/jmwright-CQ-Editor
          pip install -vvv --pre git+https://github.com/cadquery/cadquery casadi typish "multimethod>=1.11,<2.0" "nlopt>=2.9.0,<3.0" typish
          pip install pyinstaller>=5.6
          pip install path
          pip install git+https://github.com/gumyr/cq_warehouse.git#egg=cq_warehouse
          pip install git+https://github.com/gumyr/bd_warehouse
          pip install git+https://github.com/meadiode/cq_gears.git@main
          pip install -e "git+https://github.com/CadQuery/cadquery-plugins.git#egg=cq_cache&subdirectory=plugins/cq_cache"
          pip install git+https://github.com/gumyr/build123d
          pip install git+https://github.com/JustinSDK/cqMore
          pip list

      - name: Run build
        shell: bash --login -e {0}
        run: |
          micromamba activate test
          
          # ビルド実行（エラー回避のため元のコマンドライン引数を復活させます）
          BUILD_TYPE="${{ github.event.inputs.type }}"
          pyinstaller pyinstaller_pip.spec ${BUILD_TYPE:-dir}
          
          # 実行時のOCPエラー対策: Windowsのパス問題（\と/の違い）でエラーにならないよう find コマンドで確実にDLLを全コピーします
          find "$CONDA_PREFIX/Library/bin" -maxdepth 1 -name "*.dll" -exec cp {} dist/CQ-editor/ \;
          
          cp pyinstaller/CQ-editor.cmd dist/

      - name: 7zip artifact
        shell: bash --login -e {0}
        run: 7z a release.zip ./dist/*
        
      - uses: actions/upload-artifact@v4
        with:
          name: CQ-editor-Windows
          path: release.zip