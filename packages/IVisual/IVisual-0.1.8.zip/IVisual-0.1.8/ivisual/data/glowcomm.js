
var vp;
var vpVar;

define(["nbextensions/glow.1.0.min"], function() {
/*jslint plusplus: true */
console.log("glowscript loading");

window.__context = { glowscript_container: $("#glowscript").removeAttr("id") };

var scene = canvas();
var glowObjs = [];

scene.title.text("Rotating Cubes; fps = frames/sec\n ");
// Display frames per second and render time:
$("<div id='fps'/>").appendTo(scene.title);

function o2vec3(p) {
    "use strict";
    return vec(p[0], p[1], p[2]);
}

var GlowWidget = function () {
    this.comm = IPython.notebook.kernel.comm_manager.new_comm('glow');
    this.comm.on_msg($.proxy(this.handler, this));
    console.log("Comm created for glow target");
};

GlowWidget.prototype.handler = function (msg) {
    "use strict";
    var data = msg.content.data;
    //console.log('glow', data, data.length);
    //console.log('JSON ' + JSON.stringify(data));

    if (data.length > 0) {
        var i, j, k, cmd, attr, cfg, cfg2, vertdata, len2, len3, attr2, elems, elen, len4, S, b, vlst, cnvsidx;
        var trailAttrs, triangle_quad, objects, trail_cfg, make_trail;  
        var len = data.length;
        for (i = 0; i < len; i++) {
            cnvsidx = -1;
            cmd = data.shift();
            if (typeof cmd.cmd === 'undefined') {
                if (typeof cmd.idx !== 'undefined') {
                    vlst = ['pos', 'size', 'color', 'axis', 'up', 'axis_and_length', 'direction', 'texpos', 'normal', 'bumpaxis', 'center', 'forward', 'foreground', 'background', 'ambient'];
                    if (vlst.indexOf(cmd.attr) !== -1) {
                        glowObjs[cmd.idx][cmd.attr] = vec(cmd.val[0], cmd.val[1], cmd.val[2]);
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
                    vlst = ['pos', 'size', 'color', 'axis', 'up', 'axis_and_length', 'direction', 'center', 'forward', 'foreground', 'background', 'ambient'];
                    trailAttrs = ['make_trail', 'type', 'interval', 'retain'];
                    triangle_quad = ['v0', 'v1', 'v2', 'v3'];
                    len2 = cmd.attrs.length;
                    cfg = {};
                    objects = [];
                    trail_cfg = {};
                    make_trail = false;
                    for (j = 0; j < len2; j++) {
                        attr = cmd.attrs.shift();
                        if (trailAttrs.indexOf(attr.attr) !== -1) {
                            if (attr.attr === "make_trail") {
                                make_trail = attr.value;
                            } else {
                                trail_cfg[attr.attr] = attr.value;
                            }
                        } else if (vlst.indexOf(attr.attr) !== -1) {
                            cfg[attr.attr] = o2vec3(attr.value);
                        } else if (triangle_quad.indexOf(attr.attr) !== -1) {
                            cfg2 = {};
                            vertdata = attr.value;
                            len3 = vertdata.length;
                            for (k = 0; k < len3; k++) {
                                attr2 = vertdata.shift();
                                if (vlst.indexOf(attr2.attr) !== -1) {
                                    cfg2[attr2.attr] = o2vec3(attr2.value);
                                } else {
                                    cfg2[attr2.attr] = attr2.value;
                                }
                            }
                            cfg[attr.attr] = vertex(cfg2);
                        } else if (attr.attr === "canvas") {
                            cnvsidx = attr.value;
                            if (attr.value >= 0) {
                                cfg[attr.attr] = glowObjs[attr.value];
                            }
                        } else if (attr.attr === "obj_idxs") {
                            len4 = attr.value.length;
                            if (len4 > 0) {
                                for (k = 0; k < len4; k++) {
                                    objects[k] = glowObjs[attr.value[k]];
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
                            glowObjs[cmd.idx] = curve(cfg);
                            if (typeof cfg.points !== 'undefined') {
                                len3 = cfg.points.length;
                                for (j = 0; j < len3; j++) {
                                    if (typeof cfg.points[j].pos !== 'undefined') {
                                        cfg.points[j].pos = o2vec3(cfg.points[j].pos);
                                    }
                                    if (typeof cfg.points[j].color !== 'undefined') {
                                        cfg.points[j].color = o2vec3(cfg.points[j].color);
                                    }
                                }
                                glowObjs[cmd.idx].push(cfg.points);
                            }
                        } else if (cmd.cmd === 'modify') {
                            if (typeof cfg.posns !== 'undefined') {
                                len3 = cfg.posns.length;
                                for (j = 0; j < len3; j++) {
                                    glowObjs[cmd.idx].modify(j, {pos: o2vec3(cfg.posns[j])});
                                }
                            }
                            if (typeof cfg.x !== 'undefined') {
                                len3 = cfg.x.length;
                                for (j = 0; j < len3; j++) {
                                    glowObjs[cmd.idx].modify(j, {x: cfg.x[j]});
                                }
                            }
                            if (typeof cfg.y !== 'undefined') {
                                len3 = cfg.y.length;
                                for (j = 0; j < len3; j++) {
                                    glowObjs[cmd.idx].modify(j, {y: cfg.y[j]});
                                }
                            }
                            if (typeof cfg.z !== 'undefined') {
                                len3 = cfg.z.length;
                                for (j = 0; j < len3; j++) {
                                    glowObjs[cmd.idx].modify(j, {z: cfg.z[j]});
                                }
                            }
                            if (typeof cfg.red !== 'undefined') {
                                len3 = cfg.red.length;
                                S = glowObjs[cmd.idx].slice(0, len3);
                                for (j = 0; j < len3; j++) {
                                    S[j].color.x = cfg.red[j];
                                }
                            }
                            if (typeof cfg.green !== 'undefined') {
                                len3 = cfg.green.length;
                                S = glowObjs[cmd.idx].slice(0, len3);
                                for (j = 0; j < len3; j++) {
                                    S[j].color.y = cfg.green[j];
                                }
                            }
                            if (typeof cfg.blue !== 'undefined') {
                                len3 = cfg.blue.length;
                                S = glowObjs[cmd.idx].slice(0, len3);
                                for (j = 0; j < len3; j++) {
                                    S[j].color.z = cfg.blue[j];
                                }
                            }
                            if (typeof cfg.colors !== 'undefined') {
                                len3 = cfg.colors.length;
                                for (j = 0; j < len3; j++) {
                                    glowObjs[cmd.idx].modify(j, {color: o2vec3(cfg.colors[j])});
                                }
                            }
                        } else if (cmd.cmd === 'triangle') {
                            glowObjs[cmd.idx] = triangle(cfg);
                        } else if (cmd.cmd === 'quad') {
                            glowObjs[cmd.idx] = quad(cfg);
                        } else if (cmd.cmd === 'push') {
                            glowObjs[cmd.idx].push(cfg);
                        } else if (cmd.cmd === 'label') {
                            glowObjs[cmd.idx] = label(cfg);
                        } else if (cmd.cmd === 'ellipsoid') {
                            glowObjs[cmd.idx] = sphere(cfg);
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
                                for (j = 0; j < objects.length; j++) {
                                    objects[j].visible = true;
                                }
                            }
                            glowObjs[cmd.idx] = compound(objects, cfg);
                        } else if (cmd.cmd === 'canvas') {
                            glowObjs[cmd.idx] = canvas(cfg);
                            if (cfg.title !== "") {
                                glowObjs[cmd.idx].title.text(cfg.title + " \n ");
                                // Display frames per second and render time:
                                //$("<div id='fps'/>").appendTo(glowObjs[cmd.idx].title);
                            }
                        } else {
                            console.log("Unrecognized Object");
                        }
                        if (make_trail) {
                            attach_trail(glowObjs[cmd.idx], trail_cfg);
                        }
                        if ((cmd.idx >= 0) && (cnvsidx >= 0)) {
                            //glowObjs[cmd.idx].gidx = cmd.idx;
                            if (typeof glowObjs[cnvsidx] !== "undefined") {
                                var olen = glowObjs[cnvsidx].objects.length;
                                if (olen > 0) {
                                    glowObjs[cnvsidx].objects[olen - 1].gidx = cmd.idx;
                                }
                            }
                        }
                    } else {
                        console.log("Unable to create object, idx attribute is not provided");
                    }
                }
                if (cmd.cmd === 'redisplay') {
                    var c = document.getElementById(cmd.sceneId);
                    if (c !== null) {
                        var scn = "#" + cmd.sceneId;
                        glowObjs[cmd.idx].sceneclone = $(scn).clone(true,true);
                        //document.getElementById('glowscript2').appendChild(c);
                        //document.getElementById('glowscript2').replaceWith(c);
                        $('#glowscript2').replaceWith(c);
                        c = document.getElementById(cmd.sceneId);
                        var cont = scn + " .glowscript";
                        window.__context = { glowscript_container:    $(cont) };
                    } else {
                        /*
                        if (typeof glowObjs[cmd.idx].sceneclone !== 'undefined') {
                            console.log("using cloned scene");
                            $('#glowscript2').replaceWith(glowObjs[cmd.idx].sceneclone);
                        }
                        */
                        window.__context = { glowscript_container: $("#glowscript").removeAttr("id") };                    
                        var newcnvs = canvas();
                        for (var obj in glowObjs[cmd.idx].objects) {
                            var o = glowObjs[cmd.idx].objects[obj];
                            if ((o.constructor.name !== 'curve') && (o.constructor.name !== 'point')) {
                                glowObjs[o.gidx] = o.clone({canvas: newcnvs});
                                var olen = newcnvs.objects.length;
                                if (olen > 0) {
                                    newcnvs.objects[olen - 1].gidx = o.gidx;
                                }
                            }
                        }
                        glowObjs[cmd.idx] = newcnvs;
                        $("#glowscript2").attr("id",cmd.sceneId);
                    }
                } else if (cmd.cmd === 'delete') {
                    b = glowObjs[cmd.idx];
                    if ((b !== null) || (typeof b.visible !== 'undefined')) {
                        b.visible = false;
                    }
                    glowObjs[cmd.idx] = null;
                } else if (cmd.cmd === 'heartbeat') {
                    //console.log("heartbeat");
                } else if (cmd.cmd === 'push') {
                    //console.log("push detected");
                } else if (cmd.cmd === 'scene') {
                    glowObjs[cmd.idx] = scene;
                    //console.log("scene obj at idx = ", cmd.idx);
                }
            }
        }
    }
};

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

var _gaq = _gaq || [];
_gaq.push(['_setAccount', 'UA-12271543-1']);
_gaq.push(['_trackPageview']);

(function() {
    var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
    ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
    var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
})();