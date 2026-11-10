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
        shell: bash --login {0}
        run: |
          micromamba info
          # エラー対策：不足しがちなパッケージをあらかじめ追加インストール
          pip install runtype vtk ocp
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
        shell: bash --login {0}
        run: |
          micromamba activate test
          micromamba info
          BUILD_TYPE="${{ github.event.inputs.type }}"
          pyinstaller pyinstaller_pip.spec ${BUILD_TYPE:-dir}
          
          # 最終手段：Micromamba環境のDLLを、ビルドされたexeと同じフォルダにすべて強制コピーする
          cp "$CONDA_PREFIX/Library/bin/"*.dll dist/CQ-editor/
          
          cp pyinstaller/CQ-editor.cmd dist/

      - name: 7zip artifact (workaround for too many files during artifact upload)
        shell: bash --login {0}
        run: 7z a release.zip ./dist/*
        
      - uses: actions/upload-artifact@v4
        with:
          name: CQ-editor-Windows
          path: release.zip