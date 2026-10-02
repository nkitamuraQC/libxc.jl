include("libxc_bridge.jl")

rho = [0.1, 0.2, 0.3]
expected_zk = [-0.34280861, -0.43191179, -0.49441557]
out = compute_excitation_energy(rho)
println("Computed zk: ", out["zk"])