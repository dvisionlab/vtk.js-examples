r"""
    This module is a VTK Web server application.
    The following command line illustrates how to use it::

        $ vtkpython .../vtk_server.py

    Any VTK Web executable script comes with a set of standard arguments that
    can be overriden if need be::
        --host localhost
             Interface on which the HTTP server will listen.

        --port 8080
             Port number on which the HTTP server will listen.

        --content /path-to-web-content/
             Directory that you want to serve as static web content.
             By default, this variable is empty which means that we rely on another server
             to deliver the static content and the current process only focuses on the
             WebSocket connectivity of clients.

        --authKey wslink-secret
             Secret key that should be provided by the client to allow it to make any
             WebSocket communication. The client will assume if none is given that the
             server expects "wslink-secret" as the secret key.
"""

# import to process args
import sys
import os

# import vtk modules.
import vtk
from vtk.web import protocols
from vtk.web import wslink as vtk_wslink
from wslink import server

import argparse

# =============================================================================
# Create custom ServerProtocol class to handle clients requests
# =============================================================================


class _WebCone(vtk_wslink.ServerProtocol):

    # Application configuration
    view = None
    authKey = "wslink-secret"

    def initialize(self):
        global renderer, renderWindow, renderWindowInteractor, cone, mapper, actor

        # Bring used components
        self.registerVtkWebProtocol(protocols.vtkWebMouseHandler())
        self.registerVtkWebProtocol(protocols.vtkWebViewPort())
        self.registerVtkWebProtocol(protocols.vtkWebPublishImageDelivery(decode=False))
        self.registerVtkWebProtocol(protocols.vtkWebViewPortGeometryDelivery())

        # Update authentication key to use
        self.updateSecret(_WebCone.authKey)

        # tell the C++ web app to use no encoding.
        # ParaViewWebPublishImageDelivery must be set to decode=False to match.
        self.getApplication().SetImageEncoding(0)

        # Create default pipeline (Only once for all the session)
        if not _WebCone.view:
            # VTK specific code
            renderer = vtk.vtkRenderer()
            renderWindow = vtk.vtkRenderWindow()
            renderWindow.AddRenderer(renderer)

            renderWindowInteractor = vtk.vtkRenderWindowInteractor()
            renderWindowInteractor.SetRenderWindow(renderWindow)
            renderWindowInteractor.GetInteractorStyle().SetCurrentStyleToTrackballCamera()

            # cone = vtk.vtkConeSource()
            # mapper = vtk.vtkPolyDataMapper()
            # actor = vtk.vtkActor()

            # mapper.SetInputConnection(cone.GetOutputPort())
            # actor.SetMapper(mapper)

            # renderer.AddActor(actor)

            # load nrrd
            reader = vtk.vtkNrrdReader()
            reader.SetFileName('C:\\Users\\Mat\\Desktop\\tardiva3.0.nrrd')
            reader.Update()

            # The volume will be displayed by ray-cast alpha compositing.
            # A ray-cast mapper is needed to do the ray-casting.
            # volume_mapper = vtk.vtkFixedPointVolumeRayCastMapper()
            volume_mapper = vtk.vtkSmartVolumeMapper()
            volume_mapper.SetInputConnection(reader.GetOutputPort())
            volume_mapper.SetSampleDistance(0.5)

            # The color transfer function maps voxel intensities to colors.
            # It is modality-specific, and often anatomy-specific as well.
            # The goal is to one color for flesh (between 500 and 1000)
            # and another color for bone (1150 and over).
            volume_color = vtk.vtkColorTransferFunction()
            volume_color.AddRGBPoint(0, 0.2, 0.2, 0.7)
            volume_color.AddRGBPoint(500, 240.0 / 255.0, 184.0 / 255.0, 160.0 / 255.0)
            volume_color.AddRGBPoint(1000, 240.0 / 255.0, 184.0 / 255.0, 160.0 / 255.0)
            volume_color.AddRGBPoint(1150, 1.0, 1.0, 240.0 / 255.0)  # Ivory

            # The opacity transfer function is used to control the opacity
            # of different tissue types.
            volume_scalar_opacity = vtk.vtkPiecewiseFunction()
            volume_scalar_opacity.AddPoint(0, 0.00)
            volume_scalar_opacity.AddPoint(500, 0.15)
            volume_scalar_opacity.AddPoint(1000, 0.15)
            volume_scalar_opacity.AddPoint(1150, 0.85)

            # The gradient opacity function is used to decrease the opacity
            # in the 'flat' regions of the volume while maintaining the opacity
            # at the boundaries between tissue types.  The gradient is measured
            # as the amount by which the intensity changes over unit distance.
            # For most medical data, the unit distance is 1mm.
            volume_gradient_opacity = vtk.vtkPiecewiseFunction()
            volume_gradient_opacity.AddPoint(0, 0.0)
            volume_gradient_opacity.AddPoint(90, 0.5)
            volume_gradient_opacity.AddPoint(100, 1.0)

            # The VolumeProperty attaches the color and opacity functions to the
            # volume, and sets other volume properties.  The interpolation should
            # be set to linear to do a high-quality rendering.  The ShadeOn option
            # turns on directional lighting, which will usually enhance the
            # appearance of the volume and make it look more '3D'.  However,
            # the quality of the shading depends on how accurately the gradient
            # of the volume can be calculated, and for noisy data the gradient
            # estimation will be very poor.  The impact of the shading can be
            # decreased by increasing the Ambient coefficient while decreasing
            # the Diffuse and Specular coefficient.  To increase the impact
            # of shading, decrease the Ambient and increase the Diffuse and Specular.
            volume_property = vtk.vtkVolumeProperty()
            volume_property.SetColor(volume_color)
            volume_property.SetScalarOpacity(volume_scalar_opacity)
            volume_property.SetGradientOpacity(volume_gradient_opacity)
            volume_property.SetInterpolationTypeToLinear()
            volume_property.ShadeOn()
            volume_property.SetAmbient(0.4)
            volume_property.SetDiffuse(0.6)
            volume_property.SetSpecular(0.2)

            # The vtkVolume is a vtkProp3D (like a vtkActor) and controls the position
            # and orientation of the volume in world coordinates.
            volumeActor = vtk.vtkVolume()
            volumeActor.SetMapper(volume_mapper)
            volumeActor.SetProperty(volume_property)

            # Finally, add the volume to the renderer
            renderer.AddActor(volumeActor)



            ##########################
            # renderer.AddActor(actor)

            # render 
            renderer.ResetCamera()
            renderWindow.Render()

            # VTK Web application specific
            _WebCone.view = renderWindow
            self.getApplication().GetObjectIdMap().SetActiveObject("VIEW", renderWindow)

# =============================================================================
# Main: Parse args and start server
# =============================================================================


if __name__ == "__main__":
    # Create argument parser
    parser = argparse.ArgumentParser(
        description="VTK/Web Cone web-application")

    # Add default arguments
    server.add_arguments(parser)

    # Extract arguments
    args = parser.parse_args()

    # Configure our current application
    _WebCone.authKey = args.authKey

    # Start server
    server.start_webserver(options=args, protocol=_WebCone)