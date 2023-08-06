// Compiled by ClojureScript 0.0-2268
goog.provide('tamarack.chart');
goog.require('cljs.core');
goog.require('goog.string');
goog.require('goog.string');
goog.require('tamarack.util');
goog.require('goog.string.format');
goog.require('tamarack.util');
goog.require('goog.string.format');
goog.require('clojure.string');
goog.require('tamarack.canvas');
goog.require('tamarack.canvas');
goog.require('clojure.string');
tamarack.chart.MAIN_FONT = "\"Source Sans Pro\",\"Helvetica Neue\",Helvetica,Arial,sans-serif";
tamarack.chart.all_keys_in_data = (function all_keys_in_data(data){return cljs.core.sort.call(null,cljs.core.set.call(null,cljs.core.mapcat.call(null,cljs.core.keys,cljs.core.vals.call(null,data))));
});
tamarack.chart.key_colors = new cljs.core.PersistentVector(null, 5, 5, cljs.core.PersistentVector.EMPTY_NODE, ["rgba(46, 198, 255, 0.850)","rgba(112, 191, 64, 0.850)","rgba(255, 170, 65, 0.850)","rgba(252, 89, 55, 0.900)","rgba(88, 98, 195, 0.850)"], null);
tamarack.chart.key_names = new cljs.core.PersistentArrayMap(null, 4, [new cljs.core.Keyword(null,"sql","sql",1251448786),"SQL",new cljs.core.Keyword(null,"template-render","template-render",1374360902),"Template",new cljs.core.Keyword(null,"request-count","request-count",426155899),"Requests",new cljs.core.Keyword(null,"error-count","error-count",1790949450),"Errors"], null);
tamarack.chart.readable_keyword = (function readable_keyword(key){var name = cljs.core.subs.call(null,(''+cljs.core.str.cljs$core$IFn$_invoke$arity$1(key)),(1));var words = clojure.string.split.call(null,name,"-");var cap_words = cljs.core.map.call(null,clojure.string.capitalize,words);return clojure.string.join.call(null," ",cap_words);
});
tamarack.chart.key__GT_str = (function key__GT_str(key){var or__3578__auto__ = tamarack.chart.key_names.call(null,key);if(cljs.core.truth_(or__3578__auto__))
{return or__3578__auto__;
} else
{return tamarack.chart.readable_keyword.call(null,key);
}
});
tamarack.chart.make_base_levels = (function make_base_levels(key_order,data){var incremental_sum = (function incremental_sum(sensor_data){return cljs.core.first.call(null,cljs.core.reduce.call(null,(function (p__5054,p__5055){var vec__5056 = p__5054;var acc = cljs.core.nth.call(null,vec__5056,(0),null);var sum = cljs.core.nth.call(null,vec__5056,(1),null);var vec__5057 = p__5055;var key = cljs.core.nth.call(null,vec__5057,(0),null);var val = cljs.core.nth.call(null,vec__5057,(1),null);return new cljs.core.PersistentVector(null, 2, 5, cljs.core.PersistentVector.EMPTY_NODE, [cljs.core.assoc.call(null,acc,key,sum),(sum + val)], null);
}),new cljs.core.PersistentVector(null, 2, 5, cljs.core.PersistentVector.EMPTY_NODE, [cljs.core.PersistentArrayMap.EMPTY,(0)], null),cljs.core.map.call(null,(function (key){return new cljs.core.PersistentVector(null, 2, 5, cljs.core.PersistentVector.EMPTY_NODE, [key,sensor_data.call(null,key)], null);
}),key_order)));
});
return cljs.core.zipmap.call(null,cljs.core.keys.call(null,data),cljs.core.map.call(null,incremental_sum,cljs.core.vals.call(null,data)));
});
tamarack.chart.draw_data = (function draw_data(ctx,canvas_width,canvas_height,data,from,to){var margin_left = (40);var margin_right = (30);var margin_top = (20);var margin_bottom = (40);var width = ((canvas_width - margin_left) - margin_right);var height = ((canvas_height - margin_top) - margin_bottom);var all_keys = tamarack.chart.all_keys_in_data.call(null,data);var minutes = tamarack.util.minutes_between.call(null,from,to);var base_levels = tamarack.chart.make_base_levels.call(null,all_keys,data);var max_data = cljs.core.apply.call(null,cljs.core.max,(0),cljs.core.map.call(null,((function (margin_left,margin_right,margin_top,margin_bottom,width,height,all_keys,minutes,base_levels){
return (function (p__5114){var vec__5115 = p__5114;var _ = cljs.core.nth.call(null,vec__5115,(0),null);var v = cljs.core.nth.call(null,vec__5115,(1),null);return cljs.core.reduce.call(null,cljs.core._PLUS_,(0),cljs.core.vals.call(null,v));
});})(margin_left,margin_right,margin_top,margin_bottom,width,height,all_keys,minutes,base_levels))
,data));var total_minutes = (cljs.core.count.call(null,minutes) - (1));var step_width = (width / total_minutes);var step_height = (((max_data === (0)))?(0):(height / max_data));var y_ticks = (5);var map__5122_5170 = new cljs.core.PersistentArrayMap(null, 1, [new cljs.core.Keyword(null,"fill","fill",883462889),"#fff"], null);var map__5122_5171__$1 = ((cljs.core.seq_QMARK_.call(null,map__5122_5170))?cljs.core.apply.call(null,cljs.core.hash_map,map__5122_5170):map__5122_5170);var font5121_5172 = cljs.core.get.call(null,map__5122_5171__$1,new cljs.core.Keyword(null,"font","font",-1506159249));var line_dash5120_5173 = cljs.core.get.call(null,map__5122_5171__$1,new cljs.core.Keyword(null,"line-dash","line-dash",1945730248));var begin_path5118_5174 = cljs.core.get.call(null,map__5122_5171__$1,new cljs.core.Keyword(null,"begin-path","begin-path",-558487303));var line_width5119_5175 = cljs.core.get.call(null,map__5122_5171__$1,new cljs.core.Keyword(null,"line-width","line-width",-906934988));var fill5116_5176 = cljs.core.get.call(null,map__5122_5171__$1,new cljs.core.Keyword(null,"fill","fill",883462889));var stroke5117_5177 = cljs.core.get.call(null,map__5122_5171__$1,new cljs.core.Keyword(null,"stroke","stroke",1741823555));tamarack.canvas._STAR_ctx_STAR_.save();
if(cljs.core.truth_(fill5116_5176))
{tamarack.canvas._STAR_ctx_STAR_.fillStyle = fill5116_5176;
} else
{}
if(cljs.core.truth_(stroke5117_5177))
{tamarack.canvas._STAR_ctx_STAR_.strokeStyle = stroke5117_5177;
} else
{}
if(cljs.core.truth_(begin_path5118_5174))
{tamarack.canvas._STAR_ctx_STAR_.beginPath();
} else
{}
if(cljs.core.truth_(line_width5119_5175))
{tamarack.canvas._STAR_ctx_STAR_.lineWidth = line_width5119_5175;
} else
{}
if(cljs.core.truth_(line_dash5120_5173))
{tamarack.canvas._STAR_ctx_STAR_.setLineDash(line_dash5120_5173);
} else
{}
if(cljs.core.truth_(font5121_5172))
{tamarack.canvas._STAR_ctx_STAR_.font = font5121_5172;
} else
{}
ctx.fillRect((0),(0),canvas_width,canvas_height);
tamarack.canvas._STAR_ctx_STAR_.restore();
tamarack.canvas._STAR_ctx_STAR_.save();
tamarack.canvas._STAR_ctx_STAR_.translate(margin_left,margin_top);
var map__5129_5178 = new cljs.core.PersistentArrayMap(null, 6, [new cljs.core.Keyword(null,"begin-path","begin-path",-558487303),true,new cljs.core.Keyword(null,"stroke","stroke",1741823555),"rgb(187, 187, 187)",new cljs.core.Keyword(null,"fill","fill",883462889),"rgb(117, 117, 117)",new cljs.core.Keyword(null,"line-width","line-width",-906934988),0.5,new cljs.core.Keyword(null,"line-dash","line-dash",1945730248),[(2),(2)],new cljs.core.Keyword(null,"font","font",-1506159249),("10px "+cljs.core.str.cljs$core$IFn$_invoke$arity$1(tamarack.chart.MAIN_FONT))], null);var map__5129_5179__$1 = ((cljs.core.seq_QMARK_.call(null,map__5129_5178))?cljs.core.apply.call(null,cljs.core.hash_map,map__5129_5178):map__5129_5178);var fill5123_5180 = cljs.core.get.call(null,map__5129_5179__$1,new cljs.core.Keyword(null,"fill","fill",883462889));var line_dash5127_5181 = cljs.core.get.call(null,map__5129_5179__$1,new cljs.core.Keyword(null,"line-dash","line-dash",1945730248));var stroke5124_5182 = cljs.core.get.call(null,map__5129_5179__$1,new cljs.core.Keyword(null,"stroke","stroke",1741823555));var line_width5126_5183 = cljs.core.get.call(null,map__5129_5179__$1,new cljs.core.Keyword(null,"line-width","line-width",-906934988));var font5128_5184 = cljs.core.get.call(null,map__5129_5179__$1,new cljs.core.Keyword(null,"font","font",-1506159249));var begin_path5125_5185 = cljs.core.get.call(null,map__5129_5179__$1,new cljs.core.Keyword(null,"begin-path","begin-path",-558487303));tamarack.canvas._STAR_ctx_STAR_.save();
if(cljs.core.truth_(fill5123_5180))
{tamarack.canvas._STAR_ctx_STAR_.fillStyle = fill5123_5180;
} else
{}
if(cljs.core.truth_(stroke5124_5182))
{tamarack.canvas._STAR_ctx_STAR_.strokeStyle = stroke5124_5182;
} else
{}
if(cljs.core.truth_(begin_path5125_5185))
{tamarack.canvas._STAR_ctx_STAR_.beginPath();
} else
{}
if(cljs.core.truth_(line_width5126_5183))
{tamarack.canvas._STAR_ctx_STAR_.lineWidth = line_width5126_5183;
} else
{}
if(cljs.core.truth_(line_dash5127_5181))
{tamarack.canvas._STAR_ctx_STAR_.setLineDash(line_dash5127_5181);
} else
{}
if(cljs.core.truth_(font5128_5184))
{tamarack.canvas._STAR_ctx_STAR_.font = font5128_5184;
} else
{}
var n__4434__auto___5186 = (((step_height === (0)))?(1):y_ticks);var tick_idx_5187 = (0);while(true){
if((tick_idx_5187 < n__4434__auto___5186))
{var tick_val_5188 = (tick_idx_5187 * (max_data / (y_ticks - (1))));var tick_y_5189 = Math.round((height - (tick_val_5188 * step_height)));var tick_val_round_5190 = goog.string.format("%.2f",tick_val_5188);var text_measure_5191 = ctx.measureText(tick_val_round_5190);var text_width_5192 = (text_measure_5191["width"]);var text_x_5193 = (((0) - text_width_5192) - (8));var text_y_5194 = (tick_y_5189 + (3));tamarack.canvas.move_to.call(null,0.5,(0.5 + tick_y_5189));
tamarack.canvas.line_to.call(null,(0.5 + width),(0.5 + tick_y_5189));
tamarack.canvas.fill_text.call(null,tick_val_round_5190,text_x_5193,text_y_5194);
{
var G__5195 = (tick_idx_5187 + (1));
tick_idx_5187 = G__5195;
continue;
}
} else
{}
break;
}
tamarack.canvas.stroke.call(null);
tamarack.canvas._STAR_ctx_STAR_.restore();
var draw_single_point = ((function (margin_left,margin_right,margin_top,margin_bottom,width,height,all_keys,minutes,base_levels,max_data,total_minutes,step_width,step_height,y_ticks){
return (function draw_single_point(key,i,t){var x = (i * step_width);var y = (height - ((key.call(null,base_levels.call(null,t)) + key.call(null,data.call(null,t))) * step_height));return new cljs.core.PersistentVector(null, 2, 5, cljs.core.PersistentVector.EMPTY_NODE, [x,y], null);
});})(margin_left,margin_right,margin_top,margin_bottom,width,height,all_keys,minutes,base_levels,max_data,total_minutes,step_width,step_height,y_ticks))
;
var draw_inverse_point = ((function (margin_left,margin_right,margin_top,margin_bottom,width,height,all_keys,minutes,base_levels,max_data,total_minutes,step_width,step_height,y_ticks){
return (function draw_inverse_point(key,i,t){var x = (((cljs.core.count.call(null,minutes) - i) - (1)) * step_width);var y = (height - (key.call(null,base_levels.call(null,t)) * step_height));return new cljs.core.PersistentVector(null, 2, 5, cljs.core.PersistentVector.EMPTY_NODE, [x,y], null);
});})(margin_left,margin_right,margin_top,margin_bottom,width,height,all_keys,minutes,base_levels,max_data,total_minutes,step_width,step_height,y_ticks))
;
var seq__5130_5196 = cljs.core.seq.call(null,cljs.core.map.call(null,cljs.core.vector,all_keys,cljs.core.cycle.call(null,tamarack.chart.key_colors)));var chunk__5131_5197 = null;var count__5132_5198 = (0);var i__5133_5199 = (0);while(true){
if((i__5133_5199 < count__5132_5198))
{var vec__5134_5200 = cljs.core._nth.call(null,chunk__5131_5197,i__5133_5199);var key_5201 = cljs.core.nth.call(null,vec__5134_5200,(0),null);var color_5202 = cljs.core.nth.call(null,vec__5134_5200,(1),null);var polygon_5203 = new cljs.core.PersistentArrayMap(null, 2, [new cljs.core.Keyword(null,"fill","fill",883462889),color_5202,new cljs.core.Keyword(null,"points","points",-1486596883),cljs.core.concat.call(null,cljs.core.map_indexed.call(null,cljs.core.partial.call(null,draw_single_point,key_5201),minutes),cljs.core.map_indexed.call(null,cljs.core.partial.call(null,draw_inverse_point,key_5201),cljs.core.reverse.call(null,minutes)))], null);tamarack.canvas.draw_polygon.call(null,polygon_5203);
{
var G__5204 = seq__5130_5196;
var G__5205 = chunk__5131_5197;
var G__5206 = count__5132_5198;
var G__5207 = (i__5133_5199 + (1));
seq__5130_5196 = G__5204;
chunk__5131_5197 = G__5205;
count__5132_5198 = G__5206;
i__5133_5199 = G__5207;
continue;
}
} else
{var temp__4126__auto___5208 = cljs.core.seq.call(null,seq__5130_5196);if(temp__4126__auto___5208)
{var seq__5130_5209__$1 = temp__4126__auto___5208;if(cljs.core.chunked_seq_QMARK_.call(null,seq__5130_5209__$1))
{var c__4334__auto___5210 = cljs.core.chunk_first.call(null,seq__5130_5209__$1);{
var G__5211 = cljs.core.chunk_rest.call(null,seq__5130_5209__$1);
var G__5212 = c__4334__auto___5210;
var G__5213 = cljs.core.count.call(null,c__4334__auto___5210);
var G__5214 = (0);
seq__5130_5196 = G__5211;
chunk__5131_5197 = G__5212;
count__5132_5198 = G__5213;
i__5133_5199 = G__5214;
continue;
}
} else
{var vec__5135_5215 = cljs.core.first.call(null,seq__5130_5209__$1);var key_5216 = cljs.core.nth.call(null,vec__5135_5215,(0),null);var color_5217 = cljs.core.nth.call(null,vec__5135_5215,(1),null);var polygon_5218 = new cljs.core.PersistentArrayMap(null, 2, [new cljs.core.Keyword(null,"fill","fill",883462889),color_5217,new cljs.core.Keyword(null,"points","points",-1486596883),cljs.core.concat.call(null,cljs.core.map_indexed.call(null,cljs.core.partial.call(null,draw_single_point,key_5216),minutes),cljs.core.map_indexed.call(null,cljs.core.partial.call(null,draw_inverse_point,key_5216),cljs.core.reverse.call(null,minutes)))], null);tamarack.canvas.draw_polygon.call(null,polygon_5218);
{
var G__5219 = cljs.core.next.call(null,seq__5130_5209__$1);
var G__5220 = null;
var G__5221 = (0);
var G__5222 = (0);
seq__5130_5196 = G__5219;
chunk__5131_5197 = G__5220;
count__5132_5198 = G__5221;
i__5133_5199 = G__5222;
continue;
}
}
} else
{}
}
break;
}
var seq__5136_5223 = cljs.core.seq.call(null,cljs.core.map.call(null,cljs.core.vector,all_keys,cljs.core.cycle.call(null,tamarack.chart.key_colors),cljs.core.range.call(null)));var chunk__5137_5224 = null;var count__5138_5225 = (0);var i__5139_5226 = (0);while(true){
if((i__5139_5226 < count__5138_5225))
{var vec__5140_5227 = cljs.core._nth.call(null,chunk__5137_5224,i__5139_5226);var key_5228 = cljs.core.nth.call(null,vec__5140_5227,(0),null);var color_5229 = cljs.core.nth.call(null,vec__5140_5227,(1),null);var index_5230 = cljs.core.nth.call(null,vec__5140_5227,(2),null);var x_5231 = ((index_5230 * (61)) - (margin_left / (2)));var y_5232 = (height + (15));var map__5147_5233 = new cljs.core.PersistentArrayMap(null, 2, [new cljs.core.Keyword(null,"begin-path","begin-path",-558487303),true,new cljs.core.Keyword(null,"fill","fill",883462889),color_5229], null);var map__5147_5234__$1 = ((cljs.core.seq_QMARK_.call(null,map__5147_5233))?cljs.core.apply.call(null,cljs.core.hash_map,map__5147_5233):map__5147_5233);var font5146_5235 = cljs.core.get.call(null,map__5147_5234__$1,new cljs.core.Keyword(null,"font","font",-1506159249));var begin_path5143_5236 = cljs.core.get.call(null,map__5147_5234__$1,new cljs.core.Keyword(null,"begin-path","begin-path",-558487303));var fill5141_5237 = cljs.core.get.call(null,map__5147_5234__$1,new cljs.core.Keyword(null,"fill","fill",883462889));var line_dash5145_5238 = cljs.core.get.call(null,map__5147_5234__$1,new cljs.core.Keyword(null,"line-dash","line-dash",1945730248));var stroke5142_5239 = cljs.core.get.call(null,map__5147_5234__$1,new cljs.core.Keyword(null,"stroke","stroke",1741823555));var line_width5144_5240 = cljs.core.get.call(null,map__5147_5234__$1,new cljs.core.Keyword(null,"line-width","line-width",-906934988));tamarack.canvas._STAR_ctx_STAR_.save();
if(cljs.core.truth_(fill5141_5237))
{tamarack.canvas._STAR_ctx_STAR_.fillStyle = fill5141_5237;
} else
{}
if(cljs.core.truth_(stroke5142_5239))
{tamarack.canvas._STAR_ctx_STAR_.strokeStyle = stroke5142_5239;
} else
{}
if(cljs.core.truth_(begin_path5143_5236))
{tamarack.canvas._STAR_ctx_STAR_.beginPath();
} else
{}
if(cljs.core.truth_(line_width5144_5240))
{tamarack.canvas._STAR_ctx_STAR_.lineWidth = line_width5144_5240;
} else
{}
if(cljs.core.truth_(line_dash5145_5238))
{tamarack.canvas._STAR_ctx_STAR_.setLineDash(line_dash5145_5238);
} else
{}
if(cljs.core.truth_(font5146_5235))
{tamarack.canvas._STAR_ctx_STAR_.font = font5146_5235;
} else
{}
tamarack.canvas.rect.call(null,x_5231,y_5232,(12),(12));
tamarack.canvas.fill.call(null);
tamarack.canvas._STAR_ctx_STAR_.restore();
var map__5154_5241 = new cljs.core.PersistentArrayMap(null, 3, [new cljs.core.Keyword(null,"begin-path","begin-path",-558487303),true,new cljs.core.Keyword(null,"fill","fill",883462889),"rgb(117, 117, 117)",new cljs.core.Keyword(null,"font","font",-1506159249),("10px "+cljs.core.str.cljs$core$IFn$_invoke$arity$1(tamarack.chart.MAIN_FONT))], null);var map__5154_5242__$1 = ((cljs.core.seq_QMARK_.call(null,map__5154_5241))?cljs.core.apply.call(null,cljs.core.hash_map,map__5154_5241):map__5154_5241);var font5153_5243 = cljs.core.get.call(null,map__5154_5242__$1,new cljs.core.Keyword(null,"font","font",-1506159249));var fill5148_5244 = cljs.core.get.call(null,map__5154_5242__$1,new cljs.core.Keyword(null,"fill","fill",883462889));var begin_path5150_5245 = cljs.core.get.call(null,map__5154_5242__$1,new cljs.core.Keyword(null,"begin-path","begin-path",-558487303));var line_width5151_5246 = cljs.core.get.call(null,map__5154_5242__$1,new cljs.core.Keyword(null,"line-width","line-width",-906934988));var line_dash5152_5247 = cljs.core.get.call(null,map__5154_5242__$1,new cljs.core.Keyword(null,"line-dash","line-dash",1945730248));var stroke5149_5248 = cljs.core.get.call(null,map__5154_5242__$1,new cljs.core.Keyword(null,"stroke","stroke",1741823555));tamarack.canvas._STAR_ctx_STAR_.save();
if(cljs.core.truth_(fill5148_5244))
{tamarack.canvas._STAR_ctx_STAR_.fillStyle = fill5148_5244;
} else
{}
if(cljs.core.truth_(stroke5149_5248))
{tamarack.canvas._STAR_ctx_STAR_.strokeStyle = stroke5149_5248;
} else
{}
if(cljs.core.truth_(begin_path5150_5245))
{tamarack.canvas._STAR_ctx_STAR_.beginPath();
} else
{}
if(cljs.core.truth_(line_width5151_5246))
{tamarack.canvas._STAR_ctx_STAR_.lineWidth = line_width5151_5246;
} else
{}
if(cljs.core.truth_(line_dash5152_5247))
{tamarack.canvas._STAR_ctx_STAR_.setLineDash(line_dash5152_5247);
} else
{}
if(cljs.core.truth_(font5153_5243))
{tamarack.canvas._STAR_ctx_STAR_.font = font5153_5243;
} else
{}
tamarack.canvas.fill_text.call(null,tamarack.chart.key__GT_str.call(null,key_5228),(x_5231 + (16)),(y_5232 + (10)));
tamarack.canvas._STAR_ctx_STAR_.restore();
{
var G__5249 = seq__5136_5223;
var G__5250 = chunk__5137_5224;
var G__5251 = count__5138_5225;
var G__5252 = (i__5139_5226 + (1));
seq__5136_5223 = G__5249;
chunk__5137_5224 = G__5250;
count__5138_5225 = G__5251;
i__5139_5226 = G__5252;
continue;
}
} else
{var temp__4126__auto___5253 = cljs.core.seq.call(null,seq__5136_5223);if(temp__4126__auto___5253)
{var seq__5136_5254__$1 = temp__4126__auto___5253;if(cljs.core.chunked_seq_QMARK_.call(null,seq__5136_5254__$1))
{var c__4334__auto___5255 = cljs.core.chunk_first.call(null,seq__5136_5254__$1);{
var G__5256 = cljs.core.chunk_rest.call(null,seq__5136_5254__$1);
var G__5257 = c__4334__auto___5255;
var G__5258 = cljs.core.count.call(null,c__4334__auto___5255);
var G__5259 = (0);
seq__5136_5223 = G__5256;
chunk__5137_5224 = G__5257;
count__5138_5225 = G__5258;
i__5139_5226 = G__5259;
continue;
}
} else
{var vec__5155_5260 = cljs.core.first.call(null,seq__5136_5254__$1);var key_5261 = cljs.core.nth.call(null,vec__5155_5260,(0),null);var color_5262 = cljs.core.nth.call(null,vec__5155_5260,(1),null);var index_5263 = cljs.core.nth.call(null,vec__5155_5260,(2),null);var x_5264 = ((index_5263 * (61)) - (margin_left / (2)));var y_5265 = (height + (15));var map__5162_5266 = new cljs.core.PersistentArrayMap(null, 2, [new cljs.core.Keyword(null,"begin-path","begin-path",-558487303),true,new cljs.core.Keyword(null,"fill","fill",883462889),color_5262], null);var map__5162_5267__$1 = ((cljs.core.seq_QMARK_.call(null,map__5162_5266))?cljs.core.apply.call(null,cljs.core.hash_map,map__5162_5266):map__5162_5266);var begin_path5158_5268 = cljs.core.get.call(null,map__5162_5267__$1,new cljs.core.Keyword(null,"begin-path","begin-path",-558487303));var line_width5159_5269 = cljs.core.get.call(null,map__5162_5267__$1,new cljs.core.Keyword(null,"line-width","line-width",-906934988));var line_dash5160_5270 = cljs.core.get.call(null,map__5162_5267__$1,new cljs.core.Keyword(null,"line-dash","line-dash",1945730248));var font5161_5271 = cljs.core.get.call(null,map__5162_5267__$1,new cljs.core.Keyword(null,"font","font",-1506159249));var stroke5157_5272 = cljs.core.get.call(null,map__5162_5267__$1,new cljs.core.Keyword(null,"stroke","stroke",1741823555));var fill5156_5273 = cljs.core.get.call(null,map__5162_5267__$1,new cljs.core.Keyword(null,"fill","fill",883462889));tamarack.canvas._STAR_ctx_STAR_.save();
if(cljs.core.truth_(fill5156_5273))
{tamarack.canvas._STAR_ctx_STAR_.fillStyle = fill5156_5273;
} else
{}
if(cljs.core.truth_(stroke5157_5272))
{tamarack.canvas._STAR_ctx_STAR_.strokeStyle = stroke5157_5272;
} else
{}
if(cljs.core.truth_(begin_path5158_5268))
{tamarack.canvas._STAR_ctx_STAR_.beginPath();
} else
{}
if(cljs.core.truth_(line_width5159_5269))
{tamarack.canvas._STAR_ctx_STAR_.lineWidth = line_width5159_5269;
} else
{}
if(cljs.core.truth_(line_dash5160_5270))
{tamarack.canvas._STAR_ctx_STAR_.setLineDash(line_dash5160_5270);
} else
{}
if(cljs.core.truth_(font5161_5271))
{tamarack.canvas._STAR_ctx_STAR_.font = font5161_5271;
} else
{}
tamarack.canvas.rect.call(null,x_5264,y_5265,(12),(12));
tamarack.canvas.fill.call(null);
tamarack.canvas._STAR_ctx_STAR_.restore();
var map__5169_5274 = new cljs.core.PersistentArrayMap(null, 3, [new cljs.core.Keyword(null,"begin-path","begin-path",-558487303),true,new cljs.core.Keyword(null,"fill","fill",883462889),"rgb(117, 117, 117)",new cljs.core.Keyword(null,"font","font",-1506159249),("10px "+cljs.core.str.cljs$core$IFn$_invoke$arity$1(tamarack.chart.MAIN_FONT))], null);var map__5169_5275__$1 = ((cljs.core.seq_QMARK_.call(null,map__5169_5274))?cljs.core.apply.call(null,cljs.core.hash_map,map__5169_5274):map__5169_5274);var line_dash5167_5276 = cljs.core.get.call(null,map__5169_5275__$1,new cljs.core.Keyword(null,"line-dash","line-dash",1945730248));var stroke5164_5277 = cljs.core.get.call(null,map__5169_5275__$1,new cljs.core.Keyword(null,"stroke","stroke",1741823555));var fill5163_5278 = cljs.core.get.call(null,map__5169_5275__$1,new cljs.core.Keyword(null,"fill","fill",883462889));var line_width5166_5279 = cljs.core.get.call(null,map__5169_5275__$1,new cljs.core.Keyword(null,"line-width","line-width",-906934988));var font5168_5280 = cljs.core.get.call(null,map__5169_5275__$1,new cljs.core.Keyword(null,"font","font",-1506159249));var begin_path5165_5281 = cljs.core.get.call(null,map__5169_5275__$1,new cljs.core.Keyword(null,"begin-path","begin-path",-558487303));tamarack.canvas._STAR_ctx_STAR_.save();
if(cljs.core.truth_(fill5163_5278))
{tamarack.canvas._STAR_ctx_STAR_.fillStyle = fill5163_5278;
} else
{}
if(cljs.core.truth_(stroke5164_5277))
{tamarack.canvas._STAR_ctx_STAR_.strokeStyle = stroke5164_5277;
} else
{}
if(cljs.core.truth_(begin_path5165_5281))
{tamarack.canvas._STAR_ctx_STAR_.beginPath();
} else
{}
if(cljs.core.truth_(line_width5166_5279))
{tamarack.canvas._STAR_ctx_STAR_.lineWidth = line_width5166_5279;
} else
{}
if(cljs.core.truth_(line_dash5167_5276))
{tamarack.canvas._STAR_ctx_STAR_.setLineDash(line_dash5167_5276);
} else
{}
if(cljs.core.truth_(font5168_5280))
{tamarack.canvas._STAR_ctx_STAR_.font = font5168_5280;
} else
{}
tamarack.canvas.fill_text.call(null,tamarack.chart.key__GT_str.call(null,key_5261),(x_5264 + (16)),(y_5265 + (10)));
tamarack.canvas._STAR_ctx_STAR_.restore();
{
var G__5282 = cljs.core.next.call(null,seq__5136_5254__$1);
var G__5283 = null;
var G__5284 = (0);
var G__5285 = (0);
seq__5136_5223 = G__5282;
chunk__5137_5224 = G__5283;
count__5138_5225 = G__5284;
i__5139_5226 = G__5285;
continue;
}
}
} else
{}
}
break;
}
return tamarack.canvas._STAR_ctx_STAR_.restore();
});

//# sourceMappingURL=chart.js.map