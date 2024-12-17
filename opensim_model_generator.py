import opensim as osim

def modify_and_scale_bone_geometries(model_path, output_path, body_geometry_mapping, scale_factor=1.0, pres_mass=True):
    """
    Modify specific body geometries and scale the rest in an OpenSim model.

    Args:
        model_path (str): Path to the input OpenSim model file (.osim).
        output_path (str): Path to save the modified OpenSim model.
        body_geometry_mapping (dict): A dictionary mapping body names to new geometry files.
        scale_factor (float): Linear scaling factor for all remaining bone geometries.
    """
    # Load the OpenSim model
    model = osim.Model(model_path)
    print(f"Loaded model: {model_path}")

    # Initialize the model for scaling
    state = model.initSystem()

    # Modify specified body geometries
    for body_name, geometry_file in body_geometry_mapping.items():
        # Get the specified body
        body = model.getBodySet().get(body_name)
        print(f"Modifying geometry for body: {body_name}")

        # Access and modify the attached geometry
        model.getBodySet()
        attached_geometry = body.get_attached_geometry(0)
        #attached_geometry.set_mesh_file(geometry_file)
        #geometry = self._osimBody.upd_attached_geometry(index)
        osim.Mesh.safeDownCast(attached_geometry).set_mesh_file(geometry_file)
        print(f"Updated {body_name} geometry to: {geometry_file}")

    # Linearly scale the geometries of all other bones
    print(f"Scaling remaining geometries by a factor of {scale_factor}.")
    scale_set = osim.ScaleSet()
    for body in model.getBodySet():
        body_name = body.getName()
        if body_name not in body_geometry_mapping:
            scale = osim.Scale()
            scale.setScaleFactors(osim.Vec3(scale_factor))
            scale.setSegmentName(body.getName())
            scale_set.cloneAndAppend(scale)
            print(f"Added scale factor for body: {body.getName()}")

    # Apply scaling to the model
    model.scale(state=state, scaleSet=scale_set, preserveMassDist=pres_mass)
    print("Model scaling complete.")

    # Finalize the connections in the model
    model.finalizeConnections()

    # Save the modified model
    model.printToXML(output_path)
    print(f"Saved modified and scaled model to: {output_path}")


# Example usage
input_model = "C:/Users/lcar475/Documents/articulated-ssm_one_sided/osim_models/data/gait2392_simbody.osim"
output_model = "C:/Users/lcar475/Documents/articulated-ssm_one_sided/osim_models/RCH01.osim"

# Mapping of specific body names to their new geometry files
body_geometry_mapping = {
    "pelvis": "C:/Users/lcar475/Documents/articulated-ssm_one_sided/pred_meshes/RCH01/RCH01_predicted_mesh_right_pelvis.stl",
    "femur_r": "C:/Users/lcar475/Documents/articulated-ssm_one_sided/pred_meshes/RCH01/RCH01_predicted_mesh_right_femur.stl",
    "tibia_r": "C:/Users/lcar475/Documents/articulated-ssm_one_sided/pred_meshes/RCH01/RCH01_predicted_mesh_right_tibfib.stl"
}

# Scaling factor for all remaining bone geometries
scaling_factor = [0.9, 0.9, 0.9]  # Example: scale up by 10%

modify_and_scale_bone_geometries(input_model, output_model, body_geometry_mapping, scale_factor=scaling_factor)
