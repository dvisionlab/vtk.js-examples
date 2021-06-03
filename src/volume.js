import "regenerator-runtime/runtime";
// Load the rendering pieces we want to use (for both WebGL and WebGPU)
import "vtk.js/Sources/Rendering/Profiles/Volume";

import vtkGenericRenderWindow from "vtk.js/Sources/Rendering/Misc/GenericRenderWindow";

// Force DataAccessHelper to have access to various data source
import "vtk.js/Sources/IO/Core/DataAccessHelper/HtmlDataAccessHelper";
import "vtk.js/Sources/IO/Core/DataAccessHelper/HttpDataAccessHelper";
import "vtk.js/Sources/IO/Core/DataAccessHelper/JSZipDataAccessHelper";

import vtkVolume from "vtk.js/Sources/Rendering/Core/Volume";
import vtkVolumeMapper from "vtk.js/Sources/Rendering/Core/VolumeMapper";
import vtkHttpDataSetReader from "vtk.js/Sources/IO/Core/HttpDataSetReader";

// --- Set up our renderer ---

// const container = document.querySelector('#container');
const container = document.getElementById("viewer-2");

// We use the wrapper here to abstract out manual RenderWindow/Renderer/OpenGLRenderWindow setup
const genericRenderWindow = vtkGenericRenderWindow.newInstance();
genericRenderWindow.setContainer(container);
genericRenderWindow.resize();

const renderer = genericRenderWindow.getRenderer();
const renderWindow = genericRenderWindow.getRenderWindow();

// --- Set up the volume actor ---

const actor = vtkVolume.newInstance();
const mapper = vtkVolumeMapper.newInstance();

// tell the actor which mapper to use
actor.setMapper(mapper);

// --- load remote dataset ---

const reader = vtkHttpDataSetReader.newInstance({
  fetchGzip: true
});

// wire up the reader to the mapper
mapper.setInputConnection(reader.getOutputPort());

reader
  .setUrl("https://kitware.github.io/vtk-js/data/volume/LIDC2.vti", {
    fullPath: true,
    // compression: "zip",
    loadData: true
  })
  //   .then(() => reader.loadData())
  .then(() => {
    // --- Add volume actor to scene ---
    renderer.addVolume(actor);

    // --- Reset camera and render the scene ---
    renderer.resetCamera();
    renderWindow.render();
  });

// --- Expose globals so we can play with values in the dev console ---

global.renderWindow = renderWindow;
global.renderer = renderer;
global.actor = actor;
global.mapper = mapper;
