// Compiled by ClojureScript 0.0-2234
goog.provide('tamarack.components.chart');
goog.require('cljs.core');
goog.require('tamarack.xhr');
goog.require('sablono.core');
goog.require('tamarack.util');
goog.require('tamarack.chart');
goog.require('sablono.core');
goog.require('tamarack.util');
goog.require('tamarack.xhr');
goog.require('tamarack.canvas');
goog.require('tamarack.canvas');
goog.require('om.core');
goog.require('om.core');
goog.require('tamarack.chart');
tamarack.components.chart.draw_my_chart = (function draw_my_chart(app,owner){var vec__7001 = cljs.core.constant$keyword$23.cljs$core$IFn$_invoke$arity$1(cljs.core.constant$keyword$100.cljs$core$IFn$_invoke$arity$1(app));var from = cljs.core.nth.cljs$core$IFn$_invoke$arity$3(vec__7001,0,null);var to = cljs.core.nth.cljs$core$IFn$_invoke$arity$3(vec__7001,1,null);var canvas = owner.getDOMNode();var canvas_width = canvas.clientWidth;var canvas_height = canvas.clientHeight;var ctx = canvas.getContext("2d");var scale_factor = (function (){var or__3573__auto__ = window.devicePixelRatio;if(cljs.core.truth_(or__3573__auto__))
{return or__3573__auto__;
} else
{return 1;
}
})();var _STAR_ctx_STAR_7002 = tamarack.canvas._STAR_ctx_STAR_;try{tamarack.canvas._STAR_ctx_STAR_ = canvas.getContext("2d");
tamarack.canvas._STAR_ctx_STAR_.save();
tamarack.canvas._STAR_ctx_STAR_.scale(scale_factor,scale_factor);
tamarack.chart.draw_data(ctx,canvas_width,canvas_height,om.core.get_state.cljs$core$IFn$_invoke$arity$2(owner,cljs.core.constant$keyword$64),from,to);
ctx.restore();
return tamarack.canvas._STAR_ctx_STAR_.restore();
}finally {tamarack.canvas._STAR_ctx_STAR_ = _STAR_ctx_STAR_7002;
}});
tamarack.components.chart.fetch_data = (function fetch_data(app,owner,data_url){var vec__7004 = cljs.core.constant$keyword$23.cljs$core$IFn$_invoke$arity$1(cljs.core.constant$keyword$100.cljs$core$IFn$_invoke$arity$1(app));var from = cljs.core.nth.cljs$core$IFn$_invoke$arity$3(vec__7004,0,null);var to = cljs.core.nth.cljs$core$IFn$_invoke$arity$3(vec__7004,1,null);var url = (''+cljs.core.str.cljs$core$IFn$_invoke$arity$1(data_url)+"?from="+cljs.core.str.cljs$core$IFn$_invoke$arity$1(tamarack.util.inst__GT_iso(from))+"&to="+cljs.core.str.cljs$core$IFn$_invoke$arity$1(tamarack.util.inst__GT_iso(to)));return tamarack.xhr.send_edn(new cljs.core.PersistentArrayMap(null, 3, [cljs.core.constant$keyword$59,cljs.core.constant$keyword$56,cljs.core.constant$keyword$65,url,cljs.core.constant$keyword$63,((function (vec__7004,from,to,url){
return (function (res){return om.core.set_state_BANG_.cljs$core$IFn$_invoke$arity$3(owner,cljs.core.constant$keyword$64,res);
});})(vec__7004,from,to,url))
], null));
});
tamarack.components.chart.refresh_canvas_size = (function refresh_canvas_size(owner){var canvas = owner.getDOMNode();var parent = canvas.parentNode;var vec__7006 = tamarack.util.elem_content_size(parent);var elem_width = cljs.core.nth.cljs$core$IFn$_invoke$arity$3(vec__7006,0,null);var _ = cljs.core.nth.cljs$core$IFn$_invoke$arity$3(vec__7006,1,null);var elem_height = (elem_width * 0.6);var scale_factor = (function (){var or__3573__auto__ = window.devicePixelRatio;if(cljs.core.truth_(or__3573__auto__))
{return or__3573__auto__;
} else
{return 1;
}
})();canvas.setAttribute("style",("width: "+cljs.core.str.cljs$core$IFn$_invoke$arity$1(elem_width)+"px; height: "+cljs.core.str.cljs$core$IFn$_invoke$arity$1(elem_height)+"px; "));
canvas.setAttribute("width",(scale_factor * elem_width));
return canvas.setAttribute("height",(scale_factor * elem_height));
});
tamarack.components.chart.component = (function component(app,owner,p__7007){var map__7014 = p__7007;var map__7014__$1 = ((cljs.core.seq_QMARK_(map__7014))?cljs.core.apply.cljs$core$IFn$_invoke$arity$2(cljs.core.hash_map,map__7014):map__7014);var opts = map__7014__$1;var data_url = cljs.core.get.cljs$core$IFn$_invoke$arity$2(map__7014__$1,cljs.core.constant$keyword$125);if(typeof tamarack.components.chart.t7015 !== 'undefined')
{} else
{
/**
* @constructor
*/
tamarack.components.chart.t7015 = (function (data_url,opts,map__7014,p__7007,owner,app,component,meta7016){
this.data_url = data_url;
this.opts = opts;
this.map__7014 = map__7014;
this.p__7007 = p__7007;
this.owner = owner;
this.app = app;
this.component = component;
this.meta7016 = meta7016;
this.cljs$lang$protocol_mask$partition1$ = 0;
this.cljs$lang$protocol_mask$partition0$ = 393216;
})
tamarack.components.chart.t7015.cljs$lang$type = true;
tamarack.components.chart.t7015.cljs$lang$ctorStr = "tamarack.components.chart/t7015";
tamarack.components.chart.t7015.cljs$lang$ctorPrWriter = ((function (map__7014,map__7014__$1,opts,data_url){
return (function (this__4140__auto__,writer__4141__auto__,opt__4142__auto__){return cljs.core._write(writer__4141__auto__,"tamarack.components.chart/t7015");
});})(map__7014,map__7014__$1,opts,data_url))
;
tamarack.components.chart.t7015.prototype.om$core$IDidUpdate$ = true;
tamarack.components.chart.t7015.prototype.om$core$IDidUpdate$did_update$arity$3 = ((function (map__7014,map__7014__$1,opts,data_url){
return (function (_,___$1,___$2){var self__ = this;
var ___$3 = this;return tamarack.components.chart.draw_my_chart(self__.app,self__.owner);
});})(map__7014,map__7014__$1,opts,data_url))
;
tamarack.components.chart.t7015.prototype.om$core$IDidMount$ = true;
tamarack.components.chart.t7015.prototype.om$core$IDidMount$did_mount$arity$1 = ((function (map__7014,map__7014__$1,opts,data_url){
return (function (_){var self__ = this;
var ___$1 = this;tamarack.components.chart.refresh_canvas_size(self__.owner);
return tamarack.components.chart.draw_my_chart(self__.app,self__.owner);
});})(map__7014,map__7014__$1,opts,data_url))
;
tamarack.components.chart.t7015.prototype.om$core$IRender$ = true;
tamarack.components.chart.t7015.prototype.om$core$IRender$render$arity$1 = ((function (map__7014,map__7014__$1,opts,data_url){
return (function (_){var self__ = this;
var ___$1 = this;return React.DOM.canvas(null);
});})(map__7014,map__7014__$1,opts,data_url))
;
tamarack.components.chart.t7015.prototype.om$core$IWillUpdate$ = true;
tamarack.components.chart.t7015.prototype.om$core$IWillUpdate$will_update$arity$3 = ((function (map__7014,map__7014__$1,opts,data_url){
return (function (_,next_props,next_state){var self__ = this;
var ___$1 = this;if(cljs.core._EQ_.cljs$core$IFn$_invoke$arity$2(cljs.core.constant$keyword$100.cljs$core$IFn$_invoke$arity$1(next_props),cljs.core.constant$keyword$100.cljs$core$IFn$_invoke$arity$1(self__.app)))
{return null;
} else
{return tamarack.components.chart.fetch_data(next_props,self__.owner,self__.data_url);
}
});})(map__7014,map__7014__$1,opts,data_url))
;
tamarack.components.chart.t7015.prototype.om$core$IWillMount$ = true;
tamarack.components.chart.t7015.prototype.om$core$IWillMount$will_mount$arity$1 = ((function (map__7014,map__7014__$1,opts,data_url){
return (function (_){var self__ = this;
var ___$1 = this;return tamarack.components.chart.fetch_data(self__.app,self__.owner,self__.data_url);
});})(map__7014,map__7014__$1,opts,data_url))
;
tamarack.components.chart.t7015.prototype.om$core$IDisplayName$ = true;
tamarack.components.chart.t7015.prototype.om$core$IDisplayName$display_name$arity$1 = ((function (map__7014,map__7014__$1,opts,data_url){
return (function (_){var self__ = this;
var ___$1 = this;return "Chart";
});})(map__7014,map__7014__$1,opts,data_url))
;
tamarack.components.chart.t7015.prototype.cljs$core$IMeta$_meta$arity$1 = ((function (map__7014,map__7014__$1,opts,data_url){
return (function (_7017){var self__ = this;
var _7017__$1 = this;return self__.meta7016;
});})(map__7014,map__7014__$1,opts,data_url))
;
tamarack.components.chart.t7015.prototype.cljs$core$IWithMeta$_with_meta$arity$2 = ((function (map__7014,map__7014__$1,opts,data_url){
return (function (_7017,meta7016__$1){var self__ = this;
var _7017__$1 = this;return (new tamarack.components.chart.t7015(self__.data_url,self__.opts,self__.map__7014,self__.p__7007,self__.owner,self__.app,self__.component,meta7016__$1));
});})(map__7014,map__7014__$1,opts,data_url))
;
tamarack.components.chart.__GT_t7015 = ((function (map__7014,map__7014__$1,opts,data_url){
return (function __GT_t7015(data_url__$1,opts__$1,map__7014__$2,p__7007__$1,owner__$1,app__$1,component__$1,meta7016){return (new tamarack.components.chart.t7015(data_url__$1,opts__$1,map__7014__$2,p__7007__$1,owner__$1,app__$1,component__$1,meta7016));
});})(map__7014,map__7014__$1,opts,data_url))
;
}
return (new tamarack.components.chart.t7015(data_url,opts,map__7014__$1,p__7007,owner,app,component,null));
});
