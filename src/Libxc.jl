using PyCall
using Test

ENV["PYTHON"] = "python"

const pylibxc = pyimport("pylibxc")
const np = pyimport("numpy")

"""
    libxc_functional(name::String="lda_x", spin::String="unpolarized")

Create a LibXC functional instance through pylibxc.
"""
function libxc_functional(name::String="lda_x", spin::String="unpolarized")
    return pylibxc.LibXCFunctional(name, spin)
end

"""
    compute_excitation_energy(rho::AbstractVector{<:Real})

Run the LDA exchange functional on a density vector and return the Julia-side arrays.
"""
function compute_excitation_energy(rho::AbstractVector{<:Real})
    rho_arr = np.asarray(rho, dtype=np.float64)
    func = libxc_functional("lda_x", "unpolarized")
    inp = Dict("rho" => rho_arr)

    ret = func.compute(inp)
    zk = vec(Array(ret["zk"]))
    vrho = vec(Array(ret["vrho"]))

    return Dict(
        "zk" => zk,
        "vrho" => vrho,
    )
end

function run_runtime_test()
    rho = [0.1, 0.2, 0.3]
    out = compute_excitation_energy(rho)

    @test length(out["zk"]) == length(rho)
    @test length(out["vrho"]) == length(rho)
    @test all(isfinite, out["zk"])
    @test all(isfinite, out["vrho"])
    @test all(out["vrho"] .< 0.0)
end

function run_consistency_test()
    rho = [0.1, 0.2, 0.3]
    expected_zk = [-0.34280861, -0.43191179, -0.49441557]
    out = compute_excitation_energy(rho)

    @test isapprox(out["zk"], expected_zk; atol = 1.0e-7)
end

function main()
    run_runtime_test()
    run_consistency_test()
    println("libxc bridge tests passed")
end

if abspath(PROGRAM_FILE) == @__FILE__
    main()
end
