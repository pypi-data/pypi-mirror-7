// Compiled by ClojureScript 0.0-2234
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
tamarack.canvas.draw_polygon = (function draw_polygon(p__4946){var map__4961 = p__4946;var map__4961__$1 = ((cljs.core.seq_QMARK_.call(null,map__4961))?cljs.core.apply.call(null,cljs.core.hash_map,map__4961):map__4961);var points = cljs.core.get.call(null,map__4961__$1,new cljs.core.Keyword(null,"points","points",4326117461));var fill = cljs.core.get.call(null,map__4961__$1,new cljs.core.Keyword(null,"fill","fill",1017047285));var draw_point = ((function (map__4961,map__4961__$1,points,fill){
return (function draw_point(i,p__4965){var vec__4967 = p__4965;var x = cljs.core.nth.call(null,vec__4967,0,null);var y = cljs.core.nth.call(null,vec__4967,1,null);if(cljs.core._EQ_.call(null,i,0))
{return tamarack.canvas.move_to.call(null,x,y);
} else
{return tamarack.canvas.line_to.call(null,x,y);
}
});})(map__4961,map__4961__$1,points,fill))
;
var map__4974 = new cljs.core.PersistentArrayMap(null, 2, [new cljs.core.Keyword(null,"fill","fill",1017047285),fill,new cljs.core.Keyword(null,"begin-path","begin-path",2079785531),true], null);var map__4974__$1 = ((cljs.core.seq_QMARK_.call(null,map__4974))?cljs.core.apply.call(null,cljs.core.hash_map,map__4974):map__4974);var stroke4969 = cljs.core.get.call(null,map__4974__$1,new cljs.core.Keyword(null,"stroke","stroke",4416891306));var line_width4971 = cljs.core.get.call(null,map__4974__$1,new cljs.core.Keyword(null,"line-width","line-width",4036697631));var fill4968 = cljs.core.get.call(null,map__4974__$1,new cljs.core.Keyword(null,"fill","fill",1017047285));var line_dash4972 = cljs.core.get.call(null,map__4974__$1,new cljs.core.Keyword(null,"line-dash","line-dash",3466145085));var font4973 = cljs.core.get.call(null,map__4974__$1,new cljs.core.Keyword(null,"font","font",1017053121));var begin_path4970 = cljs.core.get.call(null,map__4974__$1,new cljs.core.Keyword(null,"begin-path","begin-path",2079785531));tamarack.canvas._STAR_ctx_STAR_.save();
if(cljs.core.truth_(fill4968))
{tamarack.canvas._STAR_ctx_STAR_.fillStyle = fill4968;
} else
{}
if(cljs.core.truth_(stroke4969))
{tamarack.canvas._STAR_ctx_STAR_.strokeStyle = stroke4969;
} else
{}
if(cljs.core.truth_(begin_path4970))
{tamarack.canvas._STAR_ctx_STAR_.beginPath();
} else
{}
if(cljs.core.truth_(line_width4971))
{tamarack.canvas._STAR_ctx_STAR_.lineWidth = line_width4971;
} else
{}
if(cljs.core.truth_(line_dash4972))
{tamarack.canvas._STAR_ctx_STAR_.setLineDash(line_dash4972);
} else
{}
if(cljs.core.truth_(font4973))
{tamarack.canvas._STAR_ctx_STAR_.font = font4973;
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