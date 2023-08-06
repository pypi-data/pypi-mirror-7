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
tamarack.chart.all_keys_in_data = (function all_keys_in_data(data){return cljs.core.sort.call(null,cljs.core.set.call(null,cljs.core.mapcat.call(null,cljs.core.keys,cljs.core.vals.call(null,data))));
});
tamarack.chart.key_colors = new cljs.core.PersistentVector(null, 5, 5, cljs.core.PersistentVector.EMPTY_NODE, ["rgba(46, 198, 255, 0.850)","rgba(112, 191, 64, 0.850)","rgba(255, 170, 65, 0.850)","rgba(252, 89, 55, 0.900)","rgba(88, 98, 195, 0.850)"], null);
tamarack.chart.key_names = new cljs.core.PersistentArrayMap(null, 4, [new cljs.core.Keyword(null,"sql","sql",1014018368),"SQL",new cljs.core.Keyword(null,"template-render","template-render",2613687739),"Template",new cljs.core.Keyword(null,"request-count","request-count",1313661891),"Requests",new cljs.core.Keyword(null,"error-count","error-count",3044115580),"Errors"], null);
tamarack.chart.readable_keyword = (function readable_keyword(key){var name = cljs.core.subs.call(null,(''+cljs.core.str.cljs$core$IFn$_invoke$arity$1(key)),1);var words = clojure.string.split.call(null,name,"-");var cap_words = cljs.core.map.call(null,clojure.string.capitalize,words);return clojure.string.join.call(null," ",cap_words);
});
tamarack.chart.key__GT_str = (function key__GT_str(key){var or__3573__auto__ = tamarack.chart.key_names.call(null,key);if(cljs.core.truth_(or__3573__auto__))
{return or__3573__auto__;
} else
{return tamarack.chart.readable_keyword.call(null,key);
}
});
tamarack.chart.make_base_levels = (function make_base_levels(key_order,data){var incremental_sum = (function incremental_sum(sensor_data){return cljs.core.first.call(null,cljs.core.reduce.call(null,(function (p__5020,p__5021){var vec__5022 = p__5020;var acc = cljs.core.nth.call(null,vec__5022,0,null);var sum = cljs.core.nth.call(null,vec__5022,1,null);var vec__5023 = p__5021;var key = cljs.core.nth.call(null,vec__5023,0,null);var val = cljs.core.nth.call(null,vec__5023,1,null);return new cljs.core.PersistentVector(null, 2, 5, cljs.core.PersistentVector.EMPTY_NODE, [cljs.core.assoc.call(null,acc,key,sum),(sum + val)], null);
}),new cljs.core.PersistentVector(null, 2, 5, cljs.core.PersistentVector.EMPTY_NODE, [cljs.core.PersistentArrayMap.EMPTY,0], null),cljs.core.map.call(null,(function (key){return new cljs.core.PersistentVector(null, 2, 5, cljs.core.PersistentVector.EMPTY_NODE, [key,sensor_data.call(null,key)], null);
}),key_order)));
});
return cljs.core.zipmap.call(null,cljs.core.keys.call(null,data),cljs.core.map.call(null,incremental_sum,cljs.core.vals.call(null,data)));
});
tamarack.chart.draw_data = (function draw_data(ctx,canvas_width,canvas_height,data,from,to){var margin_left = 40;var margin_right = 30;var margin_top = 20;var margin_bottom = 40;var width = ((canvas_width - margin_left) - margin_right);var height = ((canvas_height - margin_top) - margin_bottom);var all_keys = tamarack.chart.all_keys_in_data.call(null,data);var minutes = tamarack.util.minutes_between.call(null,from,to);var base_levels = tamarack.chart.make_base_levels.call(null,all_keys,data);var max_data = cljs.core.apply.call(null,cljs.core.max,0,cljs.core.map.call(null,((function (margin_left,margin_right,margin_top,margin_bottom,width,height,all_keys,minutes,base_levels){
return (function (p__5080){var vec__5081 = p__5080;var _ = cljs.core.nth.call(null,vec__5081,0,null);var v = cljs.core.nth.call(null,vec__5081,1,null);return cljs.core.reduce.call(null,cljs.core._PLUS_,0,cljs.core.vals.call(null,v));
});})(margin_left,margin_right,margin_top,margin_bottom,width,height,all_keys,minutes,base_levels))
,data));var total_minutes = (cljs.core.count.call(null,minutes) - 1);var step_width = (width / total_minutes);var step_height = (((max_data === 0))?0:(height / max_data));var y_ticks = 5;var map__5088_5136 = new cljs.core.PersistentArrayMap(null, 1, [new cljs.core.Keyword(null,"fill","fill",1017047285),"#fff"], null);var map__5088_5137__$1 = ((cljs.core.seq_QMARK_.call(null,map__5088_5136))?cljs.core.apply.call(null,cljs.core.hash_map,map__5088_5136):map__5088_5136);var begin_path5084_5138 = cljs.core.get.call(null,map__5088_5137__$1,new cljs.core.Keyword(null,"begin-path","begin-path",2079785531));var line_width5085_5139 = cljs.core.get.call(null,map__5088_5137__$1,new cljs.core.Keyword(null,"line-width","line-width",4036697631));var stroke5083_5140 = cljs.core.get.call(null,map__5088_5137__$1,new cljs.core.Keyword(null,"stroke","stroke",4416891306));var fill5082_5141 = cljs.core.get.call(null,map__5088_5137__$1,new cljs.core.Keyword(null,"fill","fill",1017047285));var font5087_5142 = cljs.core.get.call(null,map__5088_5137__$1,new cljs.core.Keyword(null,"font","font",1017053121));var line_dash5086_5143 = cljs.core.get.call(null,map__5088_5137__$1,new cljs.core.Keyword(null,"line-dash","line-dash",3466145085));tamarack.canvas._STAR_ctx_STAR_.save();
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
var map__5095_5144 = new cljs.core.PersistentArrayMap(null, 6, [new cljs.core.Keyword(null,"begin-path","begin-path",2079785531),true,new cljs.core.Keyword(null,"stroke","stroke",4416891306),"rgb(187, 187, 187)",new cljs.core.Keyword(null,"fill","fill",1017047285),"rgb(117, 117, 117)",new cljs.core.Keyword(null,"line-width","line-width",4036697631),0.5,new cljs.core.Keyword(null,"line-dash","line-dash",3466145085),[2,2],new cljs.core.Keyword(null,"font","font",1017053121),("10px "+cljs.core.str.cljs$core$IFn$_invoke$arity$1(tamarack.chart.MAIN_FONT))], null);var map__5095_5145__$1 = ((cljs.core.seq_QMARK_.call(null,map__5095_5144))?cljs.core.apply.call(null,cljs.core.hash_map,map__5095_5144):map__5095_5144);var font5094_5146 = cljs.core.get.call(null,map__5095_5145__$1,new cljs.core.Keyword(null,"font","font",1017053121));var line_width5092_5147 = cljs.core.get.call(null,map__5095_5145__$1,new cljs.core.Keyword(null,"line-width","line-width",4036697631));var line_dash5093_5148 = cljs.core.get.call(null,map__5095_5145__$1,new cljs.core.Keyword(null,"line-dash","line-dash",3466145085));var stroke5090_5149 = cljs.core.get.call(null,map__5095_5145__$1,new cljs.core.Keyword(null,"stroke","stroke",4416891306));var fill5089_5150 = cljs.core.get.call(null,map__5095_5145__$1,new cljs.core.Keyword(null,"fill","fill",1017047285));var begin_path5091_5151 = cljs.core.get.call(null,map__5095_5145__$1,new cljs.core.Keyword(null,"begin-path","begin-path",2079785531));tamarack.canvas._STAR_ctx_STAR_.save();
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
{var tick_val_5154 = (tick_idx_5153 * (max_data / (y_ticks - 1)));var tick_y_5155 = Math.round((height - (tick_val_5154 * step_height)));var tick_val_round_5156 = goog.string.format("%.2f",tick_val_5154);var text_measure_5157 = ctx.measureText(tick_val_round_5156);var text_width_5158 = (text_measure_5157["width"]);var text_x_5159 = ((0 - text_width_5158) - 8);var text_y_5160 = (tick_y_5155 + 3);tamarack.canvas.move_to.call(null,0.5,(0.5 + tick_y_5155));
tamarack.canvas.line_to.call(null,(0.5 + width),(0.5 + tick_y_5155));
tamarack.canvas.fill_text.call(null,tick_val_round_5156,text_x_5159,text_y_5160);
{
var G__5161 = (tick_idx_5153 + 1);
tick_idx_5153 = G__5161;
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
return (function draw_inverse_point(key,i,t){var x = (((cljs.core.count.call(null,minutes) - i) - 1) * step_width);var y = (height - (key.call(null,base_levels.call(null,t)) * step_height));return new cljs.core.PersistentVector(null, 2, 5, cljs.core.PersistentVector.EMPTY_NODE, [x,y], null);
});})(margin_left,margin_right,margin_top,margin_bottom,width,height,all_keys,minutes,base_levels,max_data,total_minutes,step_width,step_height,y_ticks))
;
var seq__5096_5162 = cljs.core.seq.call(null,cljs.core.map.call(null,cljs.core.vector,all_keys,cljs.core.cycle.call(null,tamarack.chart.key_colors)));var chunk__5097_5163 = null;var count__5098_5164 = 0;var i__5099_5165 = 0;while(true){
if((i__5099_5165 < count__5098_5164))
{var vec__5100_5166 = cljs.core._nth.call(null,chunk__5097_5163,i__5099_5165);var key_5167 = cljs.core.nth.call(null,vec__5100_5166,0,null);var color_5168 = cljs.core.nth.call(null,vec__5100_5166,1,null);var polygon_5169 = new cljs.core.PersistentArrayMap(null, 2, [new cljs.core.Keyword(null,"fill","fill",1017047285),color_5168,new cljs.core.Keyword(null,"points","points",4326117461),cljs.core.concat.call(null,cljs.core.map_indexed.call(null,cljs.core.partial.call(null,draw_single_point,key_5167),minutes),cljs.core.map_indexed.call(null,cljs.core.partial.call(null,draw_inverse_point,key_5167),cljs.core.reverse.call(null,minutes)))], null);tamarack.canvas.draw_polygon.call(null,polygon_5169);
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
{var temp__4126__auto___5174 = cljs.core.seq.call(null,seq__5096_5162);if(temp__4126__auto___5174)
{var seq__5096_5175__$1 = temp__4126__auto___5174;if(cljs.core.chunked_seq_QMARK_.call(null,seq__5096_5175__$1))
{var c__4329__auto___5176 = cljs.core.chunk_first.call(null,seq__5096_5175__$1);{
var G__5177 = cljs.core.chunk_rest.call(null,seq__5096_5175__$1);
var G__5178 = c__4329__auto___5176;
var G__5179 = cljs.core.count.call(null,c__4329__auto___5176);
var G__5180 = 0;
seq__5096_5162 = G__5177;
chunk__5097_5163 = G__5178;
count__5098_5164 = G__5179;
i__5099_5165 = G__5180;
continue;
}
} else
{var vec__5101_5181 = cljs.core.first.call(null,seq__5096_5175__$1);var key_5182 = cljs.core.nth.call(null,vec__5101_5181,0,null);var color_5183 = cljs.core.nth.call(null,vec__5101_5181,1,null);var polygon_5184 = new cljs.core.PersistentArrayMap(null, 2, [new cljs.core.Keyword(null,"fill","fill",1017047285),color_5183,new cljs.core.Keyword(null,"points","points",4326117461),cljs.core.concat.call(null,cljs.core.map_indexed.call(null,cljs.core.partial.call(null,draw_single_point,key_5182),minutes),cljs.core.map_indexed.call(null,cljs.core.partial.call(null,draw_inverse_point,key_5182),cljs.core.reverse.call(null,minutes)))], null);tamarack.canvas.draw_polygon.call(null,polygon_5184);
{
var G__5185 = cljs.core.next.call(null,seq__5096_5175__$1);
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
var seq__5102_5189 = cljs.core.seq.call(null,cljs.core.map.call(null,cljs.core.vector,all_keys,cljs.core.cycle.call(null,tamarack.chart.key_colors),cljs.core.range.call(null)));var chunk__5103_5190 = null;var count__5104_5191 = 0;var i__5105_5192 = 0;while(true){
if((i__5105_5192 < count__5104_5191))
{var vec__5106_5193 = cljs.core._nth.call(null,chunk__5103_5190,i__5105_5192);var key_5194 = cljs.core.nth.call(null,vec__5106_5193,0,null);var color_5195 = cljs.core.nth.call(null,vec__5106_5193,1,null);var index_5196 = cljs.core.nth.call(null,vec__5106_5193,2,null);var x_5197 = ((index_5196 * 61) - (margin_left / 2));var y_5198 = (height + 15);var map__5113_5199 = new cljs.core.PersistentArrayMap(null, 2, [new cljs.core.Keyword(null,"begin-path","begin-path",2079785531),true,new cljs.core.Keyword(null,"fill","fill",1017047285),color_5195], null);var map__5113_5200__$1 = ((cljs.core.seq_QMARK_.call(null,map__5113_5199))?cljs.core.apply.call(null,cljs.core.hash_map,map__5113_5199):map__5113_5199);var fill5107_5201 = cljs.core.get.call(null,map__5113_5200__$1,new cljs.core.Keyword(null,"fill","fill",1017047285));var stroke5108_5202 = cljs.core.get.call(null,map__5113_5200__$1,new cljs.core.Keyword(null,"stroke","stroke",4416891306));var begin_path5109_5203 = cljs.core.get.call(null,map__5113_5200__$1,new cljs.core.Keyword(null,"begin-path","begin-path",2079785531));var font5112_5204 = cljs.core.get.call(null,map__5113_5200__$1,new cljs.core.Keyword(null,"font","font",1017053121));var line_width5110_5205 = cljs.core.get.call(null,map__5113_5200__$1,new cljs.core.Keyword(null,"line-width","line-width",4036697631));var line_dash5111_5206 = cljs.core.get.call(null,map__5113_5200__$1,new cljs.core.Keyword(null,"line-dash","line-dash",3466145085));tamarack.canvas._STAR_ctx_STAR_.save();
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
tamarack.canvas.rect.call(null,x_5197,y_5198,12,12);
tamarack.canvas.fill.call(null);
tamarack.canvas._STAR_ctx_STAR_.restore();
var map__5120_5207 = new cljs.core.PersistentArrayMap(null, 3, [new cljs.core.Keyword(null,"begin-path","begin-path",2079785531),true,new cljs.core.Keyword(null,"fill","fill",1017047285),"rgb(117, 117, 117)",new cljs.core.Keyword(null,"font","font",1017053121),("10px "+cljs.core.str.cljs$core$IFn$_invoke$arity$1(tamarack.chart.MAIN_FONT))], null);var map__5120_5208__$1 = ((cljs.core.seq_QMARK_.call(null,map__5120_5207))?cljs.core.apply.call(null,cljs.core.hash_map,map__5120_5207):map__5120_5207);var font5119_5209 = cljs.core.get.call(null,map__5120_5208__$1,new cljs.core.Keyword(null,"font","font",1017053121));var stroke5115_5210 = cljs.core.get.call(null,map__5120_5208__$1,new cljs.core.Keyword(null,"stroke","stroke",4416891306));var line_width5117_5211 = cljs.core.get.call(null,map__5120_5208__$1,new cljs.core.Keyword(null,"line-width","line-width",4036697631));var fill5114_5212 = cljs.core.get.call(null,map__5120_5208__$1,new cljs.core.Keyword(null,"fill","fill",1017047285));var line_dash5118_5213 = cljs.core.get.call(null,map__5120_5208__$1,new cljs.core.Keyword(null,"line-dash","line-dash",3466145085));var begin_path5116_5214 = cljs.core.get.call(null,map__5120_5208__$1,new cljs.core.Keyword(null,"begin-path","begin-path",2079785531));tamarack.canvas._STAR_ctx_STAR_.save();
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
tamarack.canvas.fill_text.call(null,tamarack.chart.key__GT_str.call(null,key_5194),(x_5197 + 16),(y_5198 + 10));
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
{var temp__4126__auto___5219 = cljs.core.seq.call(null,seq__5102_5189);if(temp__4126__auto___5219)
{var seq__5102_5220__$1 = temp__4126__auto___5219;if(cljs.core.chunked_seq_QMARK_.call(null,seq__5102_5220__$1))
{var c__4329__auto___5221 = cljs.core.chunk_first.call(null,seq__5102_5220__$1);{
var G__5222 = cljs.core.chunk_rest.call(null,seq__5102_5220__$1);
var G__5223 = c__4329__auto___5221;
var G__5224 = cljs.core.count.call(null,c__4329__auto___5221);
var G__5225 = 0;
seq__5102_5189 = G__5222;
chunk__5103_5190 = G__5223;
count__5104_5191 = G__5224;
i__5105_5192 = G__5225;
continue;
}
} else
{var vec__5121_5226 = cljs.core.first.call(null,seq__5102_5220__$1);var key_5227 = cljs.core.nth.call(null,vec__5121_5226,0,null);var color_5228 = cljs.core.nth.call(null,vec__5121_5226,1,null);var index_5229 = cljs.core.nth.call(null,vec__5121_5226,2,null);var x_5230 = ((index_5229 * 61) - (margin_left / 2));var y_5231 = (height + 15);var map__5128_5232 = new cljs.core.PersistentArrayMap(null, 2, [new cljs.core.Keyword(null,"begin-path","begin-path",2079785531),true,new cljs.core.Keyword(null,"fill","fill",1017047285),color_5228], null);var map__5128_5233__$1 = ((cljs.core.seq_QMARK_.call(null,map__5128_5232))?cljs.core.apply.call(null,cljs.core.hash_map,map__5128_5232):map__5128_5232);var begin_path5124_5234 = cljs.core.get.call(null,map__5128_5233__$1,new cljs.core.Keyword(null,"begin-path","begin-path",2079785531));var font5127_5235 = cljs.core.get.call(null,map__5128_5233__$1,new cljs.core.Keyword(null,"font","font",1017053121));var fill5122_5236 = cljs.core.get.call(null,map__5128_5233__$1,new cljs.core.Keyword(null,"fill","fill",1017047285));var line_dash5126_5237 = cljs.core.get.call(null,map__5128_5233__$1,new cljs.core.Keyword(null,"line-dash","line-dash",3466145085));var stroke5123_5238 = cljs.core.get.call(null,map__5128_5233__$1,new cljs.core.Keyword(null,"stroke","stroke",4416891306));var line_width5125_5239 = cljs.core.get.call(null,map__5128_5233__$1,new cljs.core.Keyword(null,"line-width","line-width",4036697631));tamarack.canvas._STAR_ctx_STAR_.save();
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
tamarack.canvas.rect.call(null,x_5230,y_5231,12,12);
tamarack.canvas.fill.call(null);
tamarack.canvas._STAR_ctx_STAR_.restore();
var map__5135_5240 = new cljs.core.PersistentArrayMap(null, 3, [new cljs.core.Keyword(null,"begin-path","begin-path",2079785531),true,new cljs.core.Keyword(null,"fill","fill",1017047285),"rgb(117, 117, 117)",new cljs.core.Keyword(null,"font","font",1017053121),("10px "+cljs.core.str.cljs$core$IFn$_invoke$arity$1(tamarack.chart.MAIN_FONT))], null);var map__5135_5241__$1 = ((cljs.core.seq_QMARK_.call(null,map__5135_5240))?cljs.core.apply.call(null,cljs.core.hash_map,map__5135_5240):map__5135_5240);var line_dash5133_5242 = cljs.core.get.call(null,map__5135_5241__$1,new cljs.core.Keyword(null,"line-dash","line-dash",3466145085));var line_width5132_5243 = cljs.core.get.call(null,map__5135_5241__$1,new cljs.core.Keyword(null,"line-width","line-width",4036697631));var fill5129_5244 = cljs.core.get.call(null,map__5135_5241__$1,new cljs.core.Keyword(null,"fill","fill",1017047285));var font5134_5245 = cljs.core.get.call(null,map__5135_5241__$1,new cljs.core.Keyword(null,"font","font",1017053121));var stroke5130_5246 = cljs.core.get.call(null,map__5135_5241__$1,new cljs.core.Keyword(null,"stroke","stroke",4416891306));var begin_path5131_5247 = cljs.core.get.call(null,map__5135_5241__$1,new cljs.core.Keyword(null,"begin-path","begin-path",2079785531));tamarack.canvas._STAR_ctx_STAR_.save();
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
tamarack.canvas.fill_text.call(null,tamarack.chart.key__GT_str.call(null,key_5227),(x_5230 + 16),(y_5231 + 10));
tamarack.canvas._STAR_ctx_STAR_.restore();
{
var G__5248 = cljs.core.next.call(null,seq__5102_5220__$1);
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

//# sourceMappingURL=chart.js.map