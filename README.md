# This could become a pokemon one day...

## Examples overview

There are a few examples in this repo. They are listed below:
- `standalone.html`: A self-contained example that renders a cone. Useful as a playground and prototyping.
- `src/cone.js`: Same result as `standalone.html`, but using a webpack build approach. Good base for
  further application development.
- `src/cone-filter.js`: Example that demonstrates VTK.js filters.
- `src/volume.js`: Example that demonstrates basic volume rendering without transfer functions. Refer to
  the transfer function volume example for a complete rendering example.
- `src/volume-transfer.js`: Example that demonstrates basic volume rendering with transfer functions.
- `src/image-slicing.js`: Example that demonstrates volume slicing and interaction.
- `src/widgets.js`: Example that demonstrates a volume cropping widget.
- `src/cornerstone.js`: Example that demonstrates image parsing with cornerstone and how to load the volume in vtkjs.

## Building the examples

For `standalone.html`, no build instructions are required. Just load it up in your browser!

For the rest of the examples, you first must install the npm packages by running the following:
```
npm install
```

Once you've run that, you can now run one of the example projects:
- `npm run dev:cone`

Running the above commands will use the webpack-dev-server, which will watch
the transpiled files and reload the page whenever changes occur. Once run, you can see
the results at http://localhost:8080/.

## Remote rendering

In order to run remote rendering example:
`vtkpython ./vtkServer/vtk_server.py --port 1234` and open remoteRendering.html with any webServer (eg vscode liveServer or python http.server).
