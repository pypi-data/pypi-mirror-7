
var vp;
var vpVar;

define(["nbextensions/glow.1.0.min"], function() {
console.log("glowscript loading");

window.__context = { glowscript_container:    $("#glowscript").removeAttr("id") }
var scene = canvas()
var glowObjs = [];

scene.title.text("Rotating Cubes; fps = frames/sec\n ")
// Display frames per second and render time:
$("<div id='fps'/>").appendTo(scene.title)

function o2vec3(p) {
    return vec(p[0],p[1],p[2]);
}


var GlowWidget = function () {
    this.comm = IPython.notebook.kernel.comm_manager.new_comm('glow');
    this.comm.on_msg($.proxy(this.handler, this));
};

/*
var GlowWidget = function (comm) {
    this.comm = comm;
    this.comm.on_msg($.proxy(this.handler, this));
};
*/

GlowWidget.prototype.handler = function (msg) {
    var data = msg.content.data
    //console.log('glow', data, data.length);
    //console.log('JSON ' + JSON.stringify(data));

    if (data.length > 0) {
        var len = data.length;
        for (var i = 0; i < len; i++) {
            var cmd = data.shift();

            if (typeof cmd.cmd === 'undefined') {
                if (typeof cmd.idx !== 'undefined') {
                    var vlst = ['pos', 'size', 'color', 'axis', 'up', 'axis_and_length','direction'];
                    if (vlst.indexOf(cmd.attr) !== -1) {
                        glowObjs[cmd.idx][cmd.attr] = vec(cmd.val[0],cmd.val[1],cmd.val[2]);
                    } else {
                        glowObjs[cmd.idx][cmd.attr] = cmd.val;
                    }
                }
            } else {
                /*
                if (cmd.cmd !== 'heartbeat') {
                    console.log('glow', data, data.length);
                    console.log('JSON ' + JSON.stringify(data));
                }
                */
                if (typeof cmd.attrs !== 'undefined') {
                    var vlst = ['pos', 'size', 'color', 'axis', 'up', 'axis_and_length','direction'];
                    var trailAttrs = ['make_trail', 'type', 'interval', 'retain'];
                    var len2 = cmd.attrs.length;
                    var cfg = {};
                    var objects = [];
                    var trail_cfg = {};
                    var make_trail = false;
                    for (var j = 0; j < len2; j++) {
                        var attr = cmd.attrs.shift();
                        if (trailAttrs.indexOf(attr.attr) !== -1) {
                            if(attr.attr === "make_trail") {
                                make_trail = attr.value;
                            } else {
                                trail_cfg[attr.attr] = attr.value;
                            }
                        } else if (vlst.indexOf(attr.attr) !== -1) {
                            cfg[attr.attr] = o2vec3(attr.value);
                        } else if (attr.attr === "canvas") {
                            if (attr.value >= 0) {
                                cfg[attr.attr] = glowObjs[attr.value];
                            }
                        } else if (attr.attr === "obj_idxs") {
                            var len = attr.value.length;
                            if (len > 0) {
                                for (var i=0; i<len; i++) {
                                    objects[i] = glowObjs[attr.value[i]];
                                }
                            }
                        } else {
                            cfg[attr.attr] = attr.value;
                        }
                    }
                    if (typeof cmd.idx !== 'undefined') {
                        if (cmd.cmd === 'box') {
                            glowObjs[cmd.idx] = box(cfg);
                        } else if (cmd.cmd === 'sphere') {
                            glowObjs[cmd.idx] = sphere(cfg);
                        } else if (cmd.cmd === 'arrow') {
                            glowObjs[cmd.idx] = arrow(cfg);
                        } else if (cmd.cmd === 'cone') {
                            glowObjs[cmd.idx] = cone(cfg);
                        } else if (cmd.cmd === 'cylinder') {
                            glowObjs[cmd.idx] = cylinder(cfg);
                        } else if (cmd.cmd === 'helix') {
                            glowObjs[cmd.idx] = helix(cfg);
                        } else if (cmd.cmd === 'pyramid') {
                            glowObjs[cmd.idx] = pyramid(cfg);
                        } else if (cmd.cmd === 'ring') {
                            glowObjs[cmd.idx] = ring(cfg);
                        } else if (cmd.cmd === 'curve') {
                            console.log("curve : ",cfg);
                            glowObjs[cmd.idx] = curve(cfg);
                            if (typeof cfg.points !== 'undefined') {
                                var len3 = cfg.points.length;
                                for (var j = 0; j < len3; j++) {
                                    if (typeof cfg.points[j].pos !== 'undefined') {
                                        cfg.points[j].pos = o2vec3(cfg.points[j].pos);
                                    }
                                    if (typeof cfg.points[j].color !== 'undefined') {
                                        cfg.points[j].color = o2vec3(cfg.points[j].color);
                                    }
                                }
                                glowObjs[cmd.idx].push(cfg.points);
                            }
                        } else if (cmd.cmd === 'push') {
                            console.log("push : ",cfg);
                            glowObjs[cmd.idx].push(cfg);
                        } else if (cmd.cmd === 'label') {
                            glowObjs[cmd.idx] = label(cfg);
                        } else if (cmd.cmd === 'lights') {
                            glowObjs[cmd.idx] = lights(cfg);
                        } else if (cmd.cmd === 'triangle') {
                            glowObjs[cmd.idx] = triangle(cfg);
                        } else if (cmd.cmd === 'rotate') {
                            glowObjs[cmd.idx].rotate(cfg);
                        } else if (cmd.cmd === 'quad') {
                            glowObjs[cmd.idx] = quad(cfg);
                        } else if (cmd.cmd === 'local_light') {
                            glowObjs[cmd.idx] = local_light(cfg);
                        } else if (cmd.cmd === 'distant_light') {
                            glowObjs[cmd.idx] = distant_light(cfg);
                        } else if (cmd.cmd === 'compound') {
                            if (objects.length > 0) {
                                glowObjs[cmd.idx].visible = false;
                                glowObjs[cmd.idx] = null;
                                for (var i=0; i<objects.length; i++) {
                                    objects[i].visible = true;
                                }
                            }
                            glowObjs[cmd.idx] = compound(objects,cfg);
                        } else if (cmd.cmd === 'canvas') {
                            glowObjs[cmd.idx] = canvas(cfg);
                            if (cfg['title'] !== "") {
                                glowObjs[cmd.idx].title.text(cfg['title'] + " \n ");
                                // Display frames per second and render time:
                                //$("<div id='fps'/>").appendTo(glowObjs[cmd.idx].title);
                            }
                        } else {
                            console.log("Unrecognized Object");
                        }
                        if (make_trail) {
                            attach_trail(glowObjs[cmd.idx], trail_cfg);
                        }
                    } else {
                        console.log("Unable to create object, idx attribute is not provided")
                    }
                }
                if (cmd.cmd === 'delete') {
                    var b = glowObjs[cmd.idx];
                    if ((b !== null) || (typeof b.visible !== 'undefined')) {
                        b.visible = false;
                    }
                    glowObjs[cmd.idx] = null;
                } else if (cmd.cmd === 'heartbeat') {
                    console.log("heartbeat");
                } else if (cmd.cmd === 'push') {
                    console.log("push detected");
                } else if (cmd.cmd === 'scene') {
                    glowObjs[cmd.idx] = scene;
                    console.log("scene obj at idx = ",cmd.idx)
                }
            }
        }
    }
}

vp = new GlowWidget();
vpVar = setInterval(function(){heartbeat()}, 33);

//IPython.notebook.kernel.comm_manager.register_target('glow', function (comm) { vp = new GlowWidget(comm); vpVar = setInterval(function(){heartbeat()}, 33);});

});

function heartbeat() {
    vp.comm.send({method:'heartbeat'})
}

function heartbeatStopFunction() {
    clearInterval(vpVar);
}