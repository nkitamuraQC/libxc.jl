using Pkg

# このスクリプトがあるディレクトリをプロジェクトとして使用
project_dir = @__DIR__

Pkg.activate(project_dir)

# Project.toml に記載された依存パッケージをインストール
Pkg.instantiate()

println("Julia environment activated:")
println(project_dir)