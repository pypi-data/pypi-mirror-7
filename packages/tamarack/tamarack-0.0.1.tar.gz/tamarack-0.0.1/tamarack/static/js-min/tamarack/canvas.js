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
tamarack.canvas.draw_polygon = (function draw_polygon(p__4946){var map__4961 = p__4946;var map__4961__$1 = ((cljs.core.seq_QMARK_(map__4961))?cljs.core.apply.cljs$core$IFn$_invoke$arity$2(cljs.core.hash_map,map__4961):map__4961);var points = cljs.core.get.cljs$core$IFn$_invoke$arity$2(map__4961__$1,cljs.core.constant$keyword$16);var fill = cljs.core.get.cljs$core$IFn$_invoke$arity$2(map__4961__$1,cljs.core.constant$keyword$17);var draw_point = ((function (map__4961,map__4961__$1,points,fill){
return (function draw_point(i,p__4965){var vec__4967 = p__4965;var x = cljs.core.nth.cljs$core$IFn$_invoke$arity$3(vec__4967,0,null);var y = cljs.core.nth.cljs$core$IFn$_invoke$arity$3(vec__4967,1,null);if(cljs.core._EQ_.cljs$core$IFn$_invoke$arity$2(i,0))
{return tamarack.canvas.move_to(x,y);
} else
{return tamarack.canvas.line_to(x,y);
}
});})(map__4961,map__4961__$1,points,fill))
;
var map__4974 = new cljs.core.PersistentArrayMap(null, 2, [cljs.core.constant$keyword$17,fill,cljs.core.constant$keyword$18,true], null);var map__4974__$1 = ((cljs.core.seq_QMARK_(map__4974))?cljs.core.apply.cljs$core$IFn$_invoke$arity$2(cljs.core.hash_map,map__4974):map__4974);var stroke4969 = cljs.core.get.cljs$core$IFn$_invoke$arity$2(map__4974__$1,cljs.core.constant$keyword$22);var line_width4971 = cljs.core.get.cljs$core$IFn$_invoke$arity$2(map__4974__$1,cljs.core.constant$keyword$20);var fill4968 = cljs.core.get.cljs$core$IFn$_invoke$arity$2(map__4974__$1,cljs.core.constant$keyword$17);var line_dash4972 = cljs.core.get.cljs$core$IFn$_invoke$arity$2(map__4974__$1,cljs.core.constant$keyword$19);var font4973 = cljs.core.get.cljs$core$IFn$_invoke$arity$2(map__4974__$1,cljs.core.constant$keyword$21);var begin_path4970 = cljs.core.get.cljs$core$IFn$_invoke$arity$2(map__4974__$1,cljs.core.constant$keyword$18);tamarack.canvas._STAR_ctx_STAR_.save();
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
cljs.core.doall.cljs$core$IFn$_invoke$arity$1(cljs.core.map_indexed(draw_point,points));
if(cljs.core.truth_(fill))
{tamarack.canvas.fill();
} else
{}
return tamarack.canvas._STAR_ctx_STAR_.restore();
});
