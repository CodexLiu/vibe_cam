def convert_step_to_stl_with_gmsh(step_path: str, stl_path: str) -> None:
    import gmsh
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 1)
        gmsh.model.add("conv")
        gmsh.model.occ.importShapes(step_path)
        gmsh.model.occ.synchronize()
        gmsh.model.mesh.generate(2)
        gmsh.write(stl_path)
    finally:
        gmsh.finalize()


