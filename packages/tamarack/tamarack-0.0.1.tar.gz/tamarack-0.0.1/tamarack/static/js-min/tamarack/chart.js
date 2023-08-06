// Compiled by ClojureScript 0.0-2234
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
tamarack.chart.all_keys_in_data = (function all_keys_in_data(data){return cljs.core.sort.cljs$core$IFn$_invoke$arity$1(cljs.core.set(cljs.core.mapcat.cljs$core$IFn$_invoke$arity$2(cljs.core.keys,cljs.core.vals(data))));
});
tamarack.chart.key_colors = new cljs.core.PersistentVector(null, 5, 5, cljs.core.PersistentVector.EMPTY_NODE, ["rgba(46, 198, 255, 0.850)","rgba(112, 191, 64, 0.850)","rgba(255, 170, 65, 0.850)","rgba(252, 89, 55, 0.900)","rgba(88, 98, 195, 0.850)"], null);
tamarack.chart.key_names = new cljs.core.PersistentArrayMap(null, 4, [cljs.core.constant$keyword$24,"SQL",cljs.core.constant$keyword$25,"Template",cljs.core.constant$keyword$26,"Requests",cljs.core.constant$keyword$27,"Errors"], null);
tamarack.chart.readable_keyword = (function readable_keyword(key){var name = cljs.core.subs.cljs$core$IFn$_invoke$arity$2((''+cljs.core.str.cljs$core$IFn$_invoke$arity$1(key)),1);var words = clojure.string.split.cljs$core$IFn$_invoke$arity$2(name,"-");var cap_words = cljs.core.map.cljs$core$IFn$_invoke$arity$2(clojure.string.capitalize,words);return clojure.string.join.cljs$core$IFn$_invoke$arity$2(" ",cap_words);
});
tamarack.chart.key__GT_str = (function key__GT_str(key){var or__3573__auto__ = (tamarack.chart.key_names.cljs$core$IFn$_invoke$arity$1 ? tamarack.chart.key_names.cljs$core$IFn$_invoke$arity$1(key) : tamarack.chart.key_names.call(null,key));if(cljs.core.truth_(or__3573__auto__))
{return or__3573__auto__;
} else
{return tamarack.chart.readable_keyword(key);
}
});
tamarack.chart.make_base_levels = (function make_base_levels(key_order,data){var incremental_sum = (function incremental_sum(sensor_data){return cljs.core.first(cljs.core.reduce.cljs$core$IFn$_invoke$arity$3((function (p__5020,p__5021){var vec__5022 = p__5020;var acc = cljs.core.nth.cljs$core$IFn$_invoke$arity$3(vec__5022,0,null);var sum = cljs.core.nth.cljs$core$IFn$_invoke$arity$3(vec__5022,1,null);var vec__5023 = p__5021;var key = cljs.core.nth.cljs$core$IFn$_invoke$arity$3(vec__5023,0,null);var val = cljs.core.nth.cljs$core$IFn$_invoke$arity$3(vec__5023,1,null);return new cljs.core.PersistentVector(null, 2, 5, cljs.core.PersistentVector.EMPTY_NODE, [cljs.core.assoc.cljs$core$IFn$_invoke$arity$3(acc,key,sum),(sum + val)], null);
}),new cljs.core.PersistentVector(null, 2, 5, cljs.core.PersistentVector.EMPTY_NODE, [cljs.core.PersistentArrayMap.EMPTY,0], null),cljs.core.map.cljs$core$IFn$_invoke$arity$2((function (key){return new cljs.core.PersistentVector(null, 2, 5, cljs.core.PersistentVector.EMPTY_NODE, [key,(sensor_data.cljs$core$IFn$_invoke$arity$1 ? sensor_data.cljs$core$IFn$_invoke$arity$1(key) : sensor_data.call(null,key))], null);
}),key_order)));
});
return cljs.core.zipmap(cljs.core.keys(data),cljs.core.map.cljs$core$IFn$_invoke$arity$2(incremental_sum,cljs.core.vals(data)));
});
tamarack.chart.draw_data = (function draw_data(ctx,canvas_width,canvas_height,data,from,to){var margin_left = 40;var margin_right = 30;var margin_top = 20;var margin_bottom = 40;var width = ((canvas_width - margin_left) - margin_right);var height = ((canvas_height - margin_top) - margin_bottom);var all_keys = tamarack.chart.all_keys_in_data(data);var minutes = tamarack.util.minutes_between(from,to);var base_levels = tamarack.chart.make_base_levels(all_keys,data);var max_data = cljs.core.apply.cljs$core$IFn$_invoke$arity$3(cljs.core.max,0,cljs.core.map.cljs$core$IFn$_invoke$arity$2(((function (margin_left,margin_right,margin_top,margin_bottom,width,height,all_keys,minutes,base_levels){
return (function (p__5080){var vec__5081 = p__5080;var _ = cljs.core.nth.cljs$core$IFn$_invoke$arity$3(vec__5081,0,null);var v = cljs.core.nth.cljs$core$IFn$_invoke$arity$3(vec__5081,1,null);return cljs.core.reduce.cljs$core$IFn$_invoke$arity$3(cljs.core._PLUS_,0,cljs.core.vals(v));
});})(margin_left,margin_right,margin_top,margin_bottom,width,height,all_keys,minutes,base_levels))
,data));var total_minutes = (cljs.core.count(minutes) - 1);var step_width = (width / total_minutes);var step_height = (((max_data === 0))?0:(height / max_data));var y_ticks = 5;var map__5088_5136 = new cljs.core.PersistentArrayMap(null, 1, [cljs.core.constant$keyword$17,"#fff"], null);var map__5088_5137__$1 = ((cljs.core.seq_QMARK_(map__5088_5136))?cljs.core.apply.cljs$core$IFn$_invoke$arity$2(cljs.core.hash_map,map__5088_5136):map__5088_5136);var begin_path5084_5138 = cljs.core.get.cljs$core$IFn$_invoke$arity$2(map__5088_5137__$1,cljs.core.constant$keyword$18);var line_width5085_5139 = cljs.core.get.cljs$core$IFn$_invoke$arity$2(map__5088_5137__$1,cljs.core.constant$keyword$20);var stroke5083_5140 = cljs.core.get.cljs$core$IFn$_invoke$arity$2(map__5088_5137__$1,cljs.core.constant$keyword$22);var fill5082_5141 = cljs.core.get.cljs$core$IFn$_invoke$arity$2(map__5088_5137__$1,cljs.core.constant$keyword$17);var font5087_5142 = cljs.core.get.cljs$core$IFn$_invoke$arity$2(map__5088_5137__$1,cljs.core.constant$keyword$21);var line_dash5086_5143 = cljs.core.get.cljs$core$IFn$_invoke$arity$2(map__5088_5137__$1,cljs.core.constant$keyword$19);tamarack.canvas._STAR_ctx_STAR_.save();
if(cljs.core.truth_(fill5082_5141))
{tamarack.canvas._STAR_ctx_STAR_.fillStyle = fill5082_5141;
} else
{}
if(cljs.core.truth_(stroke5083_5140))
{tamarack.canvas._STAR_ctx_STAR_.strokeStyle = stroke5083_5140;
} else
{}
if(cljs.core.truth_(begin_path5084_5138))
{tamarack.canvas._STAR_ctx_STAR_.beginPath();
} else
{}
if(cljs.core.truth_(line_width5085_5139))
{tamarack.canvas._STAR_ctx_STAR_.lineWidth = line_width5085_5139;
} else
{}
if(cljs.core.truth_(line_dash5086_5143))
{tamarack.canvas._STAR_ctx_STAR_.setLineDash(line_dash5086_5143);
} else
{}
if(cljs.core.truth_(font5087_5142))
{tamarack.canvas._STAR_ctx_STAR_.font = font5087_5142;
} else
{}
ctx.fillRect(0,0,canvas_width,canvas_height);
tamarack.canvas._STAR_ctx_STAR_.restore();
tamarack.canvas._STAR_ctx_STAR_.save();
tamarack.canvas._STAR_ctx_STAR_.translate(margin_left,margin_top);
var map__5095_5144 = new cljs.core.PersistentArrayMap(null, 6, [cljs.core.constant$keyword$18,true,cljs.core.constant$keyword$22,"rgb(187, 187, 187)",cljs.core.constant$keyword$17,"rgb(117, 117, 117)",cljs.core.constant$keyword$20,0.5,cljs.core.constant$keyword$19,[2,2],cljs.core.constant$keyword$21,("10px "+cljs.core.str.cljs$core$IFn$_invoke$arity$1(tamarack.chart.MAIN_FONT))], null);var map__5095_5145__$1 = ((cljs.core.seq_QMARK_(map__5095_5144))?cljs.core.apply.cljs$core$IFn$_invoke$arity$2(cljs.core.hash_map,map__5095_5144):map__5095_5144);var font5094_5146 = cljs.core.get.cljs$core$IFn$_invoke$arity$2(map__5095_5145__$1,cljs.core.constant$keyword$21);var line_width5092_5147 = cljs.core.get.cljs$core$IFn$_invoke$arity$2(map__5095_5145__$1,cljs.core.constant$keyword$20);var line_dash5093_5148 = cljs.core.get.cljs$core$IFn$_invoke$arity$2(map__5095_5145__$1,cljs.core.constant$keyword$19);var stroke5090_5149 = cljs.core.get.cljs$core$IFn$_invoke$arity$2(map__5095_5145__$1,cljs.core.constant$keyword$22);var fill5089_5150 = cljs.core.get.cljs$core$IFn$_invoke$arity$2(map__5095_5145__$1,cljs.core.constant$keyword$17);var begin_path5091_5151 = cljs.core.get.cljs$core$IFn$_invoke$arity$2(map__5095_5145__$1,cljs.core.constant$keyword$18);tamarack.canvas._STAR_ctx_STAR_.save();
if(cljs.core.truth_(fill5089_5150))
{tamarack.canvas._STAR_ctx_STAR_.fillStyle = fill5089_5150;
} else
{}
if(cljs.core.truth_(stroke5090_5149))
{tamarack.canvas._STAR_ctx_STAR_.strokeStyle = stroke5090_5149;
} else
{}
if(cljs.core.truth_(begin_path5091_5151))
{tamarack.canvas._STAR_ctx_STAR_.beginPath();
} else
{}
if(cljs.core.truth_(line_width5092_5147))
{tamarack.canvas._STAR_ctx_STAR_.lineWidth = line_width5092_5147;
} else
{}
if(cljs.core.truth_(line_dash5093_5148))
{tamarack.canvas._STAR_ctx_STAR_.setLineDash(line_dash5093_5148);
} else
{}
if(cljs.core.truth_(font5094_5146))
{tamarack.canvas._STAR_ctx_STAR_.font = font5094_5146;
} else
{}
var n__4429__auto___5152 = (((step_height === 0))?1:y_ticks);var tick_idx_5153 = 0;while(true){
if((tick_idx_5153 < n__4429__auto___5152))
{var tick_val_5154 = (tick_idx_5153 * (max_data / (y_ticks - 1)));var tick_y_5155 = Math.round((height - (tick_val_5154 * step_height)));var tick_val_round_5156 = goog.string.format("%.2f",tick_val_5154);var text_measure_5157 = ctx.measureText(tick_val_round_5156);var text_width_5158 = (text_measure_5157["width"]);var text_x_5159 = ((0 - text_width_5158) - 8);var text_y_5160 = (tick_y_5155 + 3);tamarack.canvas.move_to(0.5,(0.5 + tick_y_5155));
tamarack.canvas.line_to((0.5 + width),(0.5 + tick_y_5155));
tamarack.canvas.fill_text(tick_val_round_5156,text_x_5159,text_y_5160);
{
var G__5161 = (tick_idx_5153 + 1);
tick_idx_5153 = G__5161;
continue;
}
} else
{}
break;
}
tamarack.canvas.stroke();
tamarack.canvas._STAR_ctx_STAR_.restore();
var draw_single_point = ((function (margin_left,margin_right,margin_top,margin_bottom,width,height,all_keys,minutes,base_levels,max_data,total_minutes,step_width,step_height,y_ticks){
return (function draw_single_point(key,i,t){var x = (i * step_width);var y = (height - (((key.cljs$core$IFn$_invoke$arity$1 ? key.cljs$core$IFn$_invoke$arity$1((base_levels.cljs$core$IFn$_invoke$arity$1 ? base_levels.cljs$core$IFn$_invoke$arity$1(t) : base_levels.call(null,t))) : key.call(null,(base_levels.cljs$core$IFn$_invoke$arity$1 ? base_levels.cljs$core$IFn$_invoke$arity$1(t) : base_levels.call(null,t)))) + (key.cljs$core$IFn$_invoke$arity$1 ? key.cljs$core$IFn$_invoke$arity$1((data.cljs$core$IFn$_invoke$arity$1 ? data.cljs$core$IFn$_invoke$arity$1(t) : data.call(null,t))) : key.call(null,(data.cljs$core$IFn$_invoke$arity$1 ? data.cljs$core$IFn$_invoke$arity$1(t) : data.call(null,t))))) * step_height));return new cljs.core.PersistentVector(null, 2, 5, cljs.core.PersistentVector.EMPTY_NODE, [x,y], null);
});})(margin_left,margin_right,margin_top,margin_bottom,width,height,all_keys,minutes,base_levels,max_data,total_minutes,step_width,step_height,y_ticks))
;
var draw_inverse_point = ((function (margin_left,margin_right,margin_top,margin_bottom,width,height,all_keys,minutes,base_levels,max_data,total_minutes,step_width,step_height,y_ticks){
return (function draw_inverse_point(key,i,t){var x = (((cljs.core.count(minutes) - i) - 1) * step_width);var y = (height - ((key.cljs$core$IFn$_invoke$arity$1 ? key.cljs$core$IFn$_invoke$arity$1((base_levels.cljs$core$IFn$_invoke$arity$1 ? base_levels.cljs$core$IFn$_invoke$arity$1(t) : base_levels.call(null,t))) : key.call(null,(base_levels.cljs$core$IFn$_invoke$arity$1 ? base_levels.cljs$core$IFn$_invoke$arity$1(t) : base_levels.call(null,t)))) * step_height));return new cljs.core.PersistentVector(null, 2, 5, cljs.core.PersistentVector.EMPTY_NODE, [x,y], null);
});})(margin_left,margin_right,margin_top,margin_bottom,width,height,all_keys,minutes,base_levels,max_data,total_minutes,step_width,step_height,y_ticks))
;
var seq__5096_5162 = cljs.core.seq(cljs.core.map.cljs$core$IFn$_invoke$arity$3(cljs.core.vector,all_keys,cljs.core.cycle(tamarack.chart.key_colors)));var chunk__5097_5163 = null;var count__5098_5164 = 0;var i__5099_5165 = 0;while(true){
if((i__5099_5165 < count__5098_5164))
{var vec__5100_5166 = chunk__5097_5163.cljs$core$IIndexed$_nth$arity$2(null,i__5099_5165);var key_5167 = cljs.core.nth.cljs$core$IFn$_invoke$arity$3(vec__5100_5166,0,null);var color_5168 = cljs.core.nth.cljs$core$IFn$_invoke$arity$3(vec__5100_5166,1,null);var polygon_5169 = new cljs.core.PersistentArrayMap(null, 2, [cljs.core.constant$keyword$17,color_5168,cljs.core.constant$keyword$16,cljs.core.concat.cljs$core$IFn$_invoke$arity$2(cljs.core.map_indexed(cljs.core.partial.cljs$core$IFn$_invoke$arity$2(draw_single_point,key_5167),minutes),cljs.core.map_indexed(cljs.core.partial.cljs$core$IFn$_invoke$arity$2(draw_inverse_point,key_5167),cljs.core.reverse(minutes)))], null);tamarack.canvas.draw_polygon(polygon_5169);
{
var G__5170 = seq__5096_5162;
var G__5171 = chunk__5097_5163;
var G__5172 = count__5098_5164;
var G__5173 = (i__5099_5165 + 1);
seq__5096_5162 = G__5170;
chunk__5097_5163 = G__5171;
count__5098_5164 = G__5172;
i__5099_5165 = G__5173;
continue;
}
} else
{var temp__4126__auto___5174 = cljs.core.seq(seq__5096_5162);if(temp__4126__auto___5174)
{var seq__5096_5175__$1 = temp__4126__auto___5174;if(cljs.core.chunked_seq_QMARK_(seq__5096_5175__$1))
{var c__4329__auto___5176 = cljs.core.chunk_first(seq__5096_5175__$1);{
var G__5177 = cljs.core.chunk_rest(seq__5096_5175__$1);
var G__5178 = c__4329__auto___5176;
var G__5179 = cljs.core.count(c__4329__auto___5176);
var G__5180 = 0;
seq__5096_5162 = G__5177;
chunk__5097_5163 = G__5178;
count__5098_5164 = G__5179;
i__5099_5165 = G__5180;
continue;
}
} else
{var vec__5101_5181 = cljs.core.first(seq__5096_5175__$1);var key_5182 = cljs.core.nth.cljs$core$IFn$_invoke$arity$3(vec__5101_5181,0,null);var color_5183 = cljs.core.nth.cljs$core$IFn$_invoke$arity$3(vec__5101_5181,1,null);var polygon_5184 = new cljs.core.PersistentArrayMap(null, 2, [cljs.core.constant$keyword$17,color_5183,cljs.core.constant$keyword$16,cljs.core.concat.cljs$core$IFn$_invoke$arity$2(cljs.core.map_indexed(cljs.core.partial.cljs$core$IFn$_invoke$arity$2(draw_single_point,key_5182),minutes),cljs.core.map_indexed(cljs.core.partial.cljs$core$IFn$_invoke$arity$2(draw_inverse_point,key_5182),cljs.core.reverse(minutes)))], null);tamarack.canvas.draw_polygon(polygon_5184);
{
var G__5185 = cljs.core.next(seq__5096_5175__$1);
var G__5186 = null;
var G__5187 = 0;
var G__5188 = 0;
seq__5096_5162 = G__5185;
chunk__5097_5163 = G__5186;
count__5098_5164 = G__5187;
i__5099_5165 = G__5188;
continue;
}
}
} else
{}
}
break;
}
var seq__5102_5189 = cljs.core.seq(cljs.core.map.cljs$core$IFn$_invoke$arity$4(cljs.core.vector,all_keys,cljs.core.cycle(tamarack.chart.key_colors),cljs.core.range.cljs$core$IFn$_invoke$arity$0()));var chunk__5103_5190 = null;var count__5104_5191 = 0;var i__5105_5192 = 0;while(true){
if((i__5105_5192 < count__5104_5191))
{var vec__5106_5193 = chunk__5103_5190.cljs$core$IIndexed$_nth$arity$2(null,i__5105_5192);var key_5194 = cljs.core.nth.cljs$core$IFn$_invoke$arity$3(vec__5106_5193,0,null);var color_5195 = cljs.core.nth.cljs$core$IFn$_invoke$arity$3(vec__5106_5193,1,null);var index_5196 = cljs.core.nth.cljs$core$IFn$_invoke$arity$3(vec__5106_5193,2,null);var x_5197 = ((index_5196 * 61) - (margin_left / 2));var y_5198 = (height + 15);var map__5113_5199 = new cljs.core.PersistentArrayMap(null, 2, [cljs.core.constant$keyword$18,true,cljs.core.constant$keyword$17,color_5195], null);var map__5113_5200__$1 = ((cljs.core.seq_QMARK_(map__5113_5199))?cljs.core.apply.cljs$core$IFn$_invoke$arity$2(cljs.core.hash_map,map__5113_5199):map__5113_5199);var fill5107_5201 = cljs.core.get.cljs$core$IFn$_invoke$arity$2(map__5113_5200__$1,cljs.core.constant$keyword$17);var stroke5108_5202 = cljs.core.get.cljs$core$IFn$_invoke$arity$2(map__5113_5200__$1,cljs.core.constant$keyword$22);var begin_path5109_5203 = cljs.core.get.cljs$core$IFn$_invoke$arity$2(map__5113_5200__$1,cljs.core.constant$keyword$18);var font5112_5204 = cljs.core.get.cljs$core$IFn$_invoke$arity$2(map__5113_5200__$1,cljs.core.constant$keyword$21);var line_width5110_5205 = cljs.core.get.cljs$core$IFn$_invoke$arity$2(map__5113_5200__$1,cljs.core.constant$keyword$20);var line_dash5111_5206 = cljs.core.get.cljs$core$IFn$_invoke$arity$2(map__5113_5200__$1,cljs.core.constant$keyword$19);tamarack.canvas._STAR_ctx_STAR_.save();
if(cljs.core.truth_(fill5107_5201))
{tamarack.canvas._STAR_ctx_STAR_.fillStyle = fill5107_5201;
} else
{}
if(cljs.core.truth_(stroke5108_5202))
{tamarack.canvas._STAR_ctx_STAR_.strokeStyle = stroke5108_5202;
} else
{}
if(cljs.core.truth_(begin_path5109_5203))
{tamarack.canvas._STAR_ctx_STAR_.beginPath();
} else
{}
if(cljs.core.truth_(line_width5110_5205))
{tamarack.canvas._STAR_ctx_STAR_.lineWidth = line_width5110_5205;
} else
{}
if(cljs.core.truth_(line_dash5111_5206))
{tamarack.canvas._STAR_ctx_STAR_.setLineDash(line_dash5111_5206);
} else
{}
if(cljs.core.truth_(font5112_5204))
{tamarack.canvas._STAR_ctx_STAR_.font = font5112_5204;
} else
{}
tamarack.canvas.rect(x_5197,y_5198,12,12);
tamarack.canvas.fill();
tamarack.canvas._STAR_ctx_STAR_.restore();
var map__5120_5207 = new cljs.core.PersistentArrayMap(null, 3, [cljs.core.constant$keyword$18,true,cljs.core.constant$keyword$17,"rgb(117, 117, 117)",cljs.core.constant$keyword$21,("10px "+cljs.core.str.cljs$core$IFn$_invoke$arity$1(tamarack.chart.MAIN_FONT))], null);var map__5120_5208__$1 = ((cljs.core.seq_QMARK_(map__5120_5207))?cljs.core.apply.cljs$core$IFn$_invoke$arity$2(cljs.core.hash_map,map__5120_5207):map__5120_5207);var font5119_5209 = cljs.core.get.cljs$core$IFn$_invoke$arity$2(map__5120_5208__$1,cljs.core.constant$keyword$21);var stroke5115_5210 = cljs.core.get.cljs$core$IFn$_invoke$arity$2(map__5120_5208__$1,cljs.core.constant$keyword$22);var line_width5117_5211 = cljs.core.get.cljs$core$IFn$_invoke$arity$2(map__5120_5208__$1,cljs.core.constant$keyword$20);var fill5114_5212 = cljs.core.get.cljs$core$IFn$_invoke$arity$2(map__5120_5208__$1,cljs.core.constant$keyword$17);var line_dash5118_5213 = cljs.core.get.cljs$core$IFn$_invoke$arity$2(map__5120_5208__$1,cljs.core.constant$keyword$19);var begin_path5116_5214 = cljs.core.get.cljs$core$IFn$_invoke$arity$2(map__5120_5208__$1,cljs.core.constant$keyword$18);tamarack.canvas._STAR_ctx_STAR_.save();
if(cljs.core.truth_(fill5114_5212))
{tamarack.canvas._STAR_ctx_STAR_.fillStyle = fill5114_5212;
} else
{}
if(cljs.core.truth_(stroke5115_5210))
{tamarack.canvas._STAR_ctx_STAR_.strokeStyle = stroke5115_5210;
} else
{}
if(cljs.core.truth_(begin_path5116_5214))
{tamarack.canvas._STAR_ctx_STAR_.beginPath();
} else
{}
if(cljs.core.truth_(line_width5117_5211))
{tamarack.canvas._STAR_ctx_STAR_.lineWidth = line_width5117_5211;
} else
{}
if(cljs.core.truth_(line_dash5118_5213))
{tamarack.canvas._STAR_ctx_STAR_.setLineDash(line_dash5118_5213);
} else
{}
if(cljs.core.truth_(font5119_5209))
{tamarack.canvas._STAR_ctx_STAR_.font = font5119_5209;
} else
{}
tamarack.canvas.fill_text(tamarack.chart.key__GT_str(key_5194),(x_5197 + 16),(y_5198 + 10));
tamarack.canvas._STAR_ctx_STAR_.restore();
{
var G__5215 = seq__5102_5189;
var G__5216 = chunk__5103_5190;
var G__5217 = count__5104_5191;
var G__5218 = (i__5105_5192 + 1);
seq__5102_5189 = G__5215;
chunk__5103_5190 = G__5216;
count__5104_5191 = G__5217;
i__5105_5192 = G__5218;
continue;
}
} else
{var temp__4126__auto___5219 = cljs.core.seq(seq__5102_5189);if(temp__4126__auto___5219)
{var seq__5102_5220__$1 = temp__4126__auto___5219;if(cljs.core.chunked_seq_QMARK_(seq__5102_5220__$1))
{var c__4329__auto___5221 = cljs.core.chunk_first(seq__5102_5220__$1);{
var G__5222 = cljs.core.chunk_rest(seq__5102_5220__$1);
var G__5223 = c__4329__auto___5221;
var G__5224 = cljs.core.count(c__4329__auto___5221);
var G__5225 = 0;
seq__5102_5189 = G__5222;
chunk__5103_5190 = G__5223;
count__5104_5191 = G__5224;
i__5105_5192 = G__5225;
continue;
}
} else
{var vec__5121_5226 = cljs.core.first(seq__5102_5220__$1);var key_5227 = cljs.core.nth.cljs$core$IFn$_invoke$arity$3(vec__5121_5226,0,null);var color_5228 = cljs.core.nth.cljs$core$IFn$_invoke$arity$3(vec__5121_5226,1,null);var index_5229 = cljs.core.nth.cljs$core$IFn$_invoke$arity$3(vec__5121_5226,2,null);var x_5230 = ((index_5229 * 61) - (margin_left / 2));var y_5231 = (height + 15);var map__5128_5232 = new cljs.core.PersistentArrayMap(null, 2, [cljs.core.constant$keyword$18,true,cljs.core.constant$keyword$17,color_5228], null);var map__5128_5233__$1 = ((cljs.core.seq_QMARK_(map__5128_5232))?cljs.core.apply.cljs$core$IFn$_invoke$arity$2(cljs.core.hash_map,map__5128_5232):map__5128_5232);var begin_path5124_5234 = cljs.core.get.cljs$core$IFn$_invoke$arity$2(map__5128_5233__$1,cljs.core.constant$keyword$18);var font5127_5235 = cljs.core.get.cljs$core$IFn$_invoke$arity$2(map__5128_5233__$1,cljs.core.constant$keyword$21);var fill5122_5236 = cljs.core.get.cljs$core$IFn$_invoke$arity$2(map__5128_5233__$1,cljs.core.constant$keyword$17);var line_dash5126_5237 = cljs.core.get.cljs$core$IFn$_invoke$arity$2(map__5128_5233__$1,cljs.core.constant$keyword$19);var stroke5123_5238 = cljs.core.get.cljs$core$IFn$_invoke$arity$2(map__5128_5233__$1,cljs.core.constant$keyword$22);var line_width5125_5239 = cljs.core.get.cljs$core$IFn$_invoke$arity$2(map__5128_5233__$1,cljs.core.constant$keyword$20);tamarack.canvas._STAR_ctx_STAR_.save();
if(cljs.core.truth_(fill5122_5236))
{tamarack.canvas._STAR_ctx_STAR_.fillStyle = fill5122_5236;
} else
{}
if(cljs.core.truth_(stroke5123_5238))
{tamarack.canvas._STAR_ctx_STAR_.strokeStyle = stroke5123_5238;
} else
{}
if(cljs.core.truth_(begin_path5124_5234))
{tamarack.canvas._STAR_ctx_STAR_.beginPath();
} else
{}
if(cljs.core.truth_(line_width5125_5239))
{tamarack.canvas._STAR_ctx_STAR_.lineWidth = line_width5125_5239;
} else
{}
if(cljs.core.truth_(line_dash5126_5237))
{tamarack.canvas._STAR_ctx_STAR_.setLineDash(line_dash5126_5237);
} else
{}
if(cljs.core.truth_(font5127_5235))
{tamarack.canvas._STAR_ctx_STAR_.font = font5127_5235;
} else
{}
tamarack.canvas.rect(x_5230,y_5231,12,12);
tamarack.canvas.fill();
tamarack.canvas._STAR_ctx_STAR_.restore();
var map__5135_5240 = new cljs.core.PersistentArrayMap(null, 3, [cljs.core.constant$keyword$18,true,cljs.core.constant$keyword$17,"rgb(117, 117, 117)",cljs.core.constant$keyword$21,("10px "+cljs.core.str.cljs$core$IFn$_invoke$arity$1(tamarack.chart.MAIN_FONT))], null);var map__5135_5241__$1 = ((cljs.core.seq_QMARK_(map__5135_5240))?cljs.core.apply.cljs$core$IFn$_invoke$arity$2(cljs.core.hash_map,map__5135_5240):map__5135_5240);var line_dash5133_5242 = cljs.core.get.cljs$core$IFn$_invoke$arity$2(map__5135_5241__$1,cljs.core.constant$keyword$19);var line_width5132_5243 = cljs.core.get.cljs$core$IFn$_invoke$arity$2(map__5135_5241__$1,cljs.core.constant$keyword$20);var fill5129_5244 = cljs.core.get.cljs$core$IFn$_invoke$arity$2(map__5135_5241__$1,cljs.core.constant$keyword$17);var font5134_5245 = cljs.core.get.cljs$core$IFn$_invoke$arity$2(map__5135_5241__$1,cljs.core.constant$keyword$21);var stroke5130_5246 = cljs.core.get.cljs$core$IFn$_invoke$arity$2(map__5135_5241__$1,cljs.core.constant$keyword$22);var begin_path5131_5247 = cljs.core.get.cljs$core$IFn$_invoke$arity$2(map__5135_5241__$1,cljs.core.constant$keyword$18);tamarack.canvas._STAR_ctx_STAR_.save();
if(cljs.core.truth_(fill5129_5244))
{tamarack.canvas._STAR_ctx_STAR_.fillStyle = fill5129_5244;
} else
{}
if(cljs.core.truth_(stroke5130_5246))
{tamarack.canvas._STAR_ctx_STAR_.strokeStyle = stroke5130_5246;
} else
{}
if(cljs.core.truth_(begin_path5131_5247))
{tamarack.canvas._STAR_ctx_STAR_.beginPath();
} else
{}
if(cljs.core.truth_(line_width5132_5243))
{tamarack.canvas._STAR_ctx_STAR_.lineWidth = line_width5132_5243;
} else
{}
if(cljs.core.truth_(line_dash5133_5242))
{tamarack.canvas._STAR_ctx_STAR_.setLineDash(line_dash5133_5242);
} else
{}
if(cljs.core.truth_(font5134_5245))
{tamarack.canvas._STAR_ctx_STAR_.font = font5134_5245;
} else
{}
tamarack.canvas.fill_text(tamarack.chart.key__GT_str(key_5227),(x_5230 + 16),(y_5231 + 10));
tamarack.canvas._STAR_ctx_STAR_.restore();
{
var G__5248 = cljs.core.next(seq__5102_5220__$1);
var G__5249 = null;
var G__5250 = 0;
var G__5251 = 0;
seq__5102_5189 = G__5248;
chunk__5103_5190 = G__5249;
count__5104_5191 = G__5250;
i__5105_5192 = G__5251;
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
