// Compiled by ClojureScript 0.0-2268
goog.provide('tamarack.canvas');
goog.require('cljs.core');
tamarack.canvas._STAR_ctx_STAR_ = null;
tamarack.canvas.move_to = (function move_to(x,y){return tamarack.canvas._STAR_ctx_STAR_.moveTo(x,y);
});
tamarack.canvas.line_to = (function line_to(x,y){return tamarack.canvas._STAR_ctx_STAR_.lineTo(x,y);
});
tamarack.canvas.rect = (function rect(x,y,w,h){return tamarack.canvas._STAR_ctx_STAR_.rect(x,y,w,h);
});
tamarack.canvas.fill_text = (function fill_text(text,x,y){return tamarack.canvas._STAR_ctx_STAR_.fillText(text,x,y);
});
tamarack.canvas.stroke = (function stroke(){return tamarack.canvas._STAR_ctx_STAR_.stroke();
});
tamarack.canvas.fill = (function fill(){return tamarack.canvas._STAR_ctx_STAR_.fill();
});
tamarack.canvas.draw_polygon = (function draw_polygon(p__4980){var map__4995 = p__4980;var map__4995__$1 = ((cljs.core.seq_QMARK_.call(null,map__4995))?cljs.core.apply.call(null,cljs.core.hash_map,map__4995):map__4995);var points = cljs.core.get.call(null,map__4995__$1,new cljs.core.Keyword(null,"points","points",-1486596883));var fill = cljs.core.get.call(null,map__4995__$1,new cljs.core.Keyword(null,"fill","fill",883462889));var draw_point = ((function (map__4995,map__4995__$1,points,fill){
return (function draw_point(i,p__4999){var vec__5001 = p__4999;var x = cljs.core.nth.call(null,vec__5001,(0),null);var y = cljs.core.nth.call(null,vec__5001,(1),null);if(cljs.core._EQ_.call(null,i,(0)))
{return tamarack.canvas.move_to.call(null,x,y);
} else
{return tamarack.canvas.line_to.call(null,x,y);
}
});})(map__4995,map__4995__$1,points,fill))
;
var map__5008 = new cljs.core.PersistentArrayMap(null, 2, [new cljs.core.Keyword(null,"fill","fill",883462889),fill,new cljs.core.Keyword(null,"begin-path","begin-path",-558487303),true], null);var map__5008__$1 = ((cljs.core.seq_QMARK_.call(null,map__5008))?cljs.core.apply.call(null,cljs.core.hash_map,map__5008):map__5008);var font5007 = cljs.core.get.call(null,map__5008__$1,new cljs.core.Keyword(null,"font","font",-1506159249));var stroke5003 = cljs.core.get.call(null,map__5008__$1,new cljs.core.Keyword(null,"stroke","stroke",1741823555));var fill5002 = cljs.core.get.call(null,map__5008__$1,new cljs.core.Keyword(null,"fill","fill",883462889));var line_width5005 = cljs.core.get.call(null,map__5008__$1,new cljs.core.Keyword(null,"line-width","line-width",-906934988));var line_dash5006 = cljs.core.get.call(null,map__5008__$1,new cljs.core.Keyword(null,"line-dash","line-dash",1945730248));var begin_path5004 = cljs.core.get.call(null,map__5008__$1,new cljs.core.Keyword(null,"begin-path","begin-path",-558487303));tamarack.canvas._STAR_ctx_STAR_.save();
if(cljs.core.truth_(fill5002))
{tamarack.canvas._STAR_ctx_STAR_.fillStyle = fill5002;
} else
{}
if(cljs.core.truth_(stroke5003))
{tamarack.canvas._STAR_ctx_STAR_.strokeStyle = stroke5003;
} else
{}
if(cljs.core.truth_(begin_path5004))
{tamarack.canvas._STAR_ctx_STAR_.beginPath();
} else
{}
if(cljs.core.truth_(line_width5005))
{tamarack.canvas._STAR_ctx_STAR_.lineWidth = line_width5005;
} else
{}
if(cljs.core.truth_(line_dash5006))
{tamarack.canvas._STAR_ctx_STAR_.setLineDash(line_dash5006);
} else
{}
if(cljs.core.truth_(font5007))
{tamarack.canvas._STAR_ctx_STAR_.font = font5007;
} else
{}
cljs.core.doall.call(null,cljs.core.map_indexed.call(null,draw_point,points));
if(cljs.core.truth_(fill))
{tamarack.canvas.fill.call(null);
} else
{}
return tamarack.canvas._STAR_ctx_STAR_.restore();
});

//# sourceMappingURL=canvas.js.map