def exportX3D(app, filename):
    print(filename)
    f = open(filename, 'w')
    f.write('Test')
    f.close()
    
def setup(app):
    app.registerExporter('Xtreme3D Editor Scene', '*.x3d', exportX3D)