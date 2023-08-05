const Cu = Components.utils;
const {devtools} = Cu.import("resource://gre/modules/devtools/Loader.jsm", {});
const {require} = devtools;
let { DebuggerServer } = Cu.import("resource://gre/modules/devtools/dbg-server.jsm", {});
let { DebuggerClient } = Cu.import("resource://gre/modules/devtools/dbg-client.jsm", {});

let gClient, gActor;
let gAppId = "YOURAPPID";

function normalizeName(name) {
  return name.replace(/[- ]+/g, '').toLowerCase();
}

function locateWithName(name, aCallback) {
  var callback = aCallback || marionetteScriptFinished;
  let apps = window.wrappedJSObject.Applications.installedApps;
  let normalizedSearchName = normalizeName(name);

  for (let manifestURL in apps) {
    let app = apps[manifestURL];
    console.log(app);
/*
    let origin = null;
    let entryPoints = app.manifest.entry_points;
    if (entryPoints) {
      for (let ep in entryPoints) {
        let currentEntryPoint = entryPoints[ep];
        let appName = currentEntryPoint.name;

        if (normalizedSearchName === GaiaApps.normalizeName(appName)) {
          return GaiaApps.sendLocateResponse(callback, app, appName, ep);
        }
      }
    } else {
      let appName = app.manifest.name;

      if (normalizedSearchName === GaiaApps.normalizeName(appName)) {
        return GaiaApps.sendLocateResponse(callback, app, appName);
      }
    }
*/
  }
  callback(false);
}  

let onDone = function () {
    locateWithName(gAppId, function uninstall(app) {
      navigator.mozApps.mgmt.uninstall(app);
      gClient.close();
      marionetteScriptFinished("finished");
    });
};

let connect = function(onDone) {
  // Initialize a loopback remote protocol connection
  if (!DebuggerServer.initialized) {
    DebuggerServer.init(function () { return true; });
    // We need to register browser actors to have `listTabs` working
    // and also have a root actor
    DebuggerServer.addBrowserActors();
  }

  // Setup the debugger client
  gClient = new DebuggerClient(DebuggerServer.connectPipe());
  gClient.connect(function onConnect() {
    gClient.listTabs(function onListTabs(aResponse) {
      gActor = aResponse.webappsActor;
      onDone();
    });
  });
};

connect(onDone);
