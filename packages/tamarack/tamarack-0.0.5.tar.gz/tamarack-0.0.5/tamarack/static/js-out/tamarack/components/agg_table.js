// Compiled by ClojureScript 0.0-2268
goog.provide('tamarack.components.agg_table');
goog.require('cljs.core');
goog.require('tamarack.xhr');
goog.require('sablono.core');
goog.require('tamarack.routes');
goog.require('tamarack.util');
goog.require('sablono.core');
goog.require('tamarack.util');
goog.require('tamarack.xhr');
goog.require('clojure.string');
goog.require('om.core');
goog.require('om.core');
goog.require('clojure.string');
goog.require('tamarack.routes');
tamarack.components.agg_table.fetch_data = (function fetch_data(app,owner,agg_type){var vec__7002 = new cljs.core.Keyword(null,"window","window",724519534).cljs$core$IFn$_invoke$arity$1(new cljs.core.Keyword(null,"timeslice","timeslice",446627929).cljs$core$IFn$_invoke$arity$1(app));var from = cljs.core.nth.call(null,vec__7002,(0),null);var to = cljs.core.nth.call(null,vec__7002,(1),null);var url = (''+cljs.core.str.cljs$core$IFn$_invoke$arity$1(clojure.string.join.call(null,"/",new cljs.core.PersistentVector(null, 4, 5, cljs.core.PersistentVector.EMPTY_NODE, ["/explorer-api/v1/applications",new cljs.core.Keyword(null,"name","name",1843675177).cljs$core$IFn$_invoke$arity$1(new cljs.core.Keyword(null,"current-app","current-app",1533042174).cljs$core$IFn$_invoke$arity$1(app)),"aggregate",cljs.core.subs.call(null,(''+cljs.core.str.cljs$core$IFn$_invoke$arity$1(agg_type)),(1))], null)))+"?from="+cljs.core.str.cljs$core$IFn$_invoke$arity$1(tamarack.util.inst__GT_iso.call(null,from))+"&to="+cljs.core.str.cljs$core$IFn$_invoke$arity$1(tamarack.util.inst__GT_iso.call(null,to)));return tamarack.xhr.send_edn.call(null,new cljs.core.PersistentArrayMap(null, 3, [new cljs.core.Keyword(null,"method","method",55703592),new cljs.core.Keyword(null,"get","get",1683182755),new cljs.core.Keyword(null,"url","url",276297046),url,new cljs.core.Keyword(null,"on-complete","on-complete",-1531183971),((function (vec__7002,from,to,url){
return (function (res){return om.core.set_state_BANG_.call(null,owner,new cljs.core.Keyword(null,"data","data",-232669377),res);
});})(vec__7002,from,to,url))
], null));
});
tamarack.components.agg_table.endpoint_url = (function endpoint_url(app,endpoint){return tamarack.routes.url_of.call(null,tamarack.routes.app_endpoint_overview,new cljs.core.PersistentArrayMap(null, 2, [new cljs.core.Keyword(null,"id","id",-1388402092),new cljs.core.Keyword(null,"name","name",1843675177).cljs$core$IFn$_invoke$arity$1(new cljs.core.Keyword(null,"current-app","current-app",1533042174).cljs$core$IFn$_invoke$arity$1(app)),new cljs.core.Keyword(null,"endpoint","endpoint",447890044),endpoint], null));
});
tamarack.components.agg_table.goto_endpoint = (function goto_endpoint(app,endpoint,e){e.preventDefault();
return tamarack.routes.navigate_to.call(null,tamarack.routes.app_endpoint_overview,new cljs.core.PersistentArrayMap(null, 2, [new cljs.core.Keyword(null,"id","id",-1388402092),new cljs.core.Keyword(null,"name","name",1843675177).cljs$core$IFn$_invoke$arity$1(new cljs.core.Keyword(null,"current-app","current-app",1533042174).cljs$core$IFn$_invoke$arity$1(cljs.core.deref.call(null,app))),new cljs.core.Keyword(null,"endpoint","endpoint",447890044),endpoint], null));
});
tamarack.components.agg_table.render_row = (function render_row(app,round_fn,unit,p__7003){var vec__7006 = p__7003;var endpoint = cljs.core.nth.call(null,vec__7006,(0),null);var value = cljs.core.nth.call(null,vec__7006,(1),null);return React.DOM.tr({"key": endpoint},React.DOM.td(null,React.DOM.a({"href": tamarack.components.agg_table.endpoint_url.call(null,app,endpoint), "onClick": cljs.core.partial.call(null,tamarack.components.agg_table.goto_endpoint,app,endpoint)},sablono.interpreter.interpret.call(null,endpoint))),(function (){var attrs7007 = (''+cljs.core.str.cljs$core$IFn$_invoke$arity$1(round_fn.call(null,value))+cljs.core.str.cljs$core$IFn$_invoke$arity$1(unit));return cljs.core.apply.call(null,React.DOM.td,((cljs.core.map_QMARK_.call(null,attrs7007))?sablono.interpreter.attributes.call(null,sablono.util.merge_with_class.call(null,new cljs.core.PersistentArrayMap(null, 1, [new cljs.core.Keyword(null,"class","class",-2030961996),new cljs.core.PersistentVector(null, 1, 5, cljs.core.PersistentVector.EMPTY_NODE, ["num-col"], null)], null),attrs7007)):{"className": "num-col"}),cljs.core.remove.call(null,cljs.core.nil_QMARK_,((cljs.core.map_QMARK_.call(null,attrs7007))?cljs.core.PersistentVector.EMPTY:new cljs.core.PersistentVector(null, 1, 5, cljs.core.PersistentVector.EMPTY_NODE, [sablono.interpreter.interpret.call(null,attrs7007)], null))));
})());
});
tamarack.components.agg_table.component = (function component(app,owner,p__7008){var map__7014 = p__7008;var map__7014__$1 = ((cljs.core.seq_QMARK_.call(null,map__7014))?cljs.core.apply.call(null,cljs.core.hash_map,map__7014):map__7014);var opts = map__7014__$1;var unit = cljs.core.get.call(null,map__7014__$1,new cljs.core.Keyword(null,"unit","unit",375175175));var round_fn = cljs.core.get.call(null,map__7014__$1,new cljs.core.Keyword(null,"round-fn","round-fn",-1368487407));var agg_type = cljs.core.get.call(null,map__7014__$1,new cljs.core.Keyword(null,"agg-type","agg-type",1621538561));if(typeof tamarack.components.agg_table.t7015 !== 'undefined')
{} else
{
/**
* @constructor
*/
tamarack.components.agg_table.t7015 = (function (agg_type,round_fn,unit,opts,map__7014,p__7008,owner,app,component,meta7016){
this.agg_type = agg_type;
this.round_fn = round_fn;
this.unit = unit;
this.opts = opts;
this.map__7014 = map__7014;
this.p__7008 = p__7008;
this.owner = owner;
this.app = app;
this.component = component;
this.meta7016 = meta7016;
this.cljs$lang$protocol_mask$partition1$ = 0;
this.cljs$lang$protocol_mask$partition0$ = 393216;
})
tamarack.components.agg_table.t7015.cljs$lang$type = true;
tamarack.components.agg_table.t7015.cljs$lang$ctorStr = "tamarack.components.agg-table/t7015";
tamarack.components.agg_table.t7015.cljs$lang$ctorPrWriter = ((function (map__7014,map__7014__$1,opts,unit,round_fn,agg_type){
return (function (this__4145__auto__,writer__4146__auto__,opt__4147__auto__){return cljs.core._write.call(null,writer__4146__auto__,"tamarack.components.agg-table/t7015");
});})(map__7014,map__7014__$1,opts,unit,round_fn,agg_type))
;
tamarack.components.agg_table.t7015.prototype.om$core$IRender$ = true;
tamarack.components.agg_table.t7015.prototype.om$core$IRender$render$arity$1 = ((function (map__7014,map__7014__$1,opts,unit,round_fn,agg_type){
return (function (_){var self__ = this;
var ___$1 = this;return React.DOM.table({"className": "table table-hover table-striped table-condensed"},(function (){var attrs7018 = cljs.core.map.call(null,cljs.core.partial.call(null,tamarack.components.agg_table.render_row,self__.app,self__.round_fn,self__.unit),om.core.get_state.call(null,self__.owner,new cljs.core.Keyword(null,"data","data",-232669377)));return cljs.core.apply.call(null,React.DOM.tbody,((cljs.core.map_QMARK_.call(null,attrs7018))?sablono.interpreter.attributes.call(null,attrs7018):null),cljs.core.remove.call(null,cljs.core.nil_QMARK_,((cljs.core.map_QMARK_.call(null,attrs7018))?cljs.core.PersistentVector.EMPTY:new cljs.core.PersistentVector(null, 1, 5, cljs.core.PersistentVector.EMPTY_NODE, [sablono.interpreter.interpret.call(null,attrs7018)], null))));
})());
});})(map__7014,map__7014__$1,opts,unit,round_fn,agg_type))
;
tamarack.components.agg_table.t7015.prototype.om$core$IWillUpdate$ = true;
tamarack.components.agg_table.t7015.prototype.om$core$IWillUpdate$will_update$arity$3 = ((function (map__7014,map__7014__$1,opts,unit,round_fn,agg_type){
return (function (_,next_props,next_state){var self__ = this;
var ___$1 = this;if(cljs.core._EQ_.call(null,new cljs.core.Keyword(null,"timeslice","timeslice",446627929).cljs$core$IFn$_invoke$arity$1(next_props),new cljs.core.Keyword(null,"timeslice","timeslice",446627929).cljs$core$IFn$_invoke$arity$1(self__.app)))
{return null;
} else
{return tamarack.components.agg_table.fetch_data.call(null,next_props,self__.owner,self__.agg_type);
}
});})(map__7014,map__7014__$1,opts,unit,round_fn,agg_type))
;
tamarack.components.agg_table.t7015.prototype.om$core$IWillMount$ = true;
tamarack.components.agg_table.t7015.prototype.om$core$IWillMount$will_mount$arity$1 = ((function (map__7014,map__7014__$1,opts,unit,round_fn,agg_type){
return (function (_){var self__ = this;
var ___$1 = this;return tamarack.components.agg_table.fetch_data.call(null,self__.app,self__.owner,self__.agg_type);
});})(map__7014,map__7014__$1,opts,unit,round_fn,agg_type))
;
tamarack.components.agg_table.t7015.prototype.om$core$IDisplayName$ = true;
tamarack.components.agg_table.t7015.prototype.om$core$IDisplayName$display_name$arity$1 = ((function (map__7014,map__7014__$1,opts,unit,round_fn,agg_type){
return (function (_){var self__ = this;
var ___$1 = this;return "AggregateTable";
});})(map__7014,map__7014__$1,opts,unit,round_fn,agg_type))
;
tamarack.components.agg_table.t7015.prototype.cljs$core$IMeta$_meta$arity$1 = ((function (map__7014,map__7014__$1,opts,unit,round_fn,agg_type){
return (function (_7017){var self__ = this;
var _7017__$1 = this;return self__.meta7016;
});})(map__7014,map__7014__$1,opts,unit,round_fn,agg_type))
;
tamarack.components.agg_table.t7015.prototype.cljs$core$IWithMeta$_with_meta$arity$2 = ((function (map__7014,map__7014__$1,opts,unit,round_fn,agg_type){
return (function (_7017,meta7016__$1){var self__ = this;
var _7017__$1 = this;return (new tamarack.components.agg_table.t7015(self__.agg_type,self__.round_fn,self__.unit,self__.opts,self__.map__7014,self__.p__7008,self__.owner,self__.app,self__.component,meta7016__$1));
});})(map__7014,map__7014__$1,opts,unit,round_fn,agg_type))
;
tamarack.components.agg_table.__GT_t7015 = ((function (map__7014,map__7014__$1,opts,unit,round_fn,agg_type){
return (function __GT_t7015(agg_type__$1,round_fn__$1,unit__$1,opts__$1,map__7014__$2,p__7008__$1,owner__$1,app__$1,component__$1,meta7016){return (new tamarack.components.agg_table.t7015(agg_type__$1,round_fn__$1,unit__$1,opts__$1,map__7014__$2,p__7008__$1,owner__$1,app__$1,component__$1,meta7016));
});})(map__7014,map__7014__$1,opts,unit,round_fn,agg_type))
;
}
return (new tamarack.components.agg_table.t7015(agg_type,round_fn,unit,opts,map__7014__$1,p__7008,owner,app,component,null));
});

//# sourceMappingURL=agg_table.js.map