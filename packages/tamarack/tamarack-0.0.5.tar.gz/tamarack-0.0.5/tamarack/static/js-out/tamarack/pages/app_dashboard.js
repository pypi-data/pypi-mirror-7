// Compiled by ClojureScript 0.0-2268
goog.provide('tamarack.pages.app_dashboard');
goog.require('cljs.core');
goog.require('tamarack.components.agg_table');
goog.require('sablono.core');
goog.require('tamarack.util');
goog.require('sablono.core');
goog.require('tamarack.util');
goog.require('tamarack.components.agg_table');
goog.require('clojure.string');
goog.require('om.core');
goog.require('om.core');
goog.require('tamarack.components.chart');
goog.require('clojure.string');
goog.require('tamarack.components.chart');
tamarack.pages.app_dashboard.app_chart_url = (function app_chart_url(app,chart_type){var comps = new cljs.core.PersistentVector(null, 4, 5, cljs.core.PersistentVector.EMPTY_NODE, ["/explorer-api/v1/applications",new cljs.core.Keyword(null,"name","name",1843675177).cljs$core$IFn$_invoke$arity$1(app),"chart",cljs.core.subs.call(null,(''+cljs.core.str.cljs$core$IFn$_invoke$arity$1(chart_type)),(1))], null);return clojure.string.join.call(null,"/",comps);
});
tamarack.pages.app_dashboard.page = (function page(app,owner){if(typeof tamarack.pages.app_dashboard.t7239 !== 'undefined')
{} else
{
/**
* @constructor
*/
tamarack.pages.app_dashboard.t7239 = (function (owner,app,page,meta7240){
this.owner = owner;
this.app = app;
this.page = page;
this.meta7240 = meta7240;
this.cljs$lang$protocol_mask$partition1$ = 0;
this.cljs$lang$protocol_mask$partition0$ = 393216;
})
tamarack.pages.app_dashboard.t7239.cljs$lang$type = true;
tamarack.pages.app_dashboard.t7239.cljs$lang$ctorStr = "tamarack.pages.app-dashboard/t7239";
tamarack.pages.app_dashboard.t7239.cljs$lang$ctorPrWriter = (function (this__4145__auto__,writer__4146__auto__,opt__4147__auto__){return cljs.core._write.call(null,writer__4146__auto__,"tamarack.pages.app-dashboard/t7239");
});
tamarack.pages.app_dashboard.t7239.prototype.om$core$IRender$ = true;
tamarack.pages.app_dashboard.t7239.prototype.om$core$IRender$render$arity$1 = (function (_){var self__ = this;
var ___$1 = this;return React.DOM.div({"className": "app-dashboard"},React.DOM.div({"className": "row"},React.DOM.div({"className": "col-md-12"},React.DOM.h2(null,"Application Overview for ",sablono.interpreter.interpret.call(null,new cljs.core.Keyword(null,"display-name","display-name",694513143).cljs$core$IFn$_invoke$arity$1(new cljs.core.Keyword(null,"current-app","current-app",1533042174).cljs$core$IFn$_invoke$arity$1(self__.app)))))),React.DOM.div({"className": "row"},React.DOM.div({"className": "col-md-12"},React.DOM.div({"className": "row"},React.DOM.div({"className": "col-md-4"},React.DOM.h3(null,"Time per Request"),sablono.interpreter.interpret.call(null,om.core.build.call(null,tamarack.components.chart.component,self__.app,new cljs.core.PersistentArrayMap(null, 1, [new cljs.core.Keyword(null,"opts","opts",155075701),new cljs.core.PersistentArrayMap(null, 1, [new cljs.core.Keyword(null,"data-url","data-url",-1627669834),tamarack.pages.app_dashboard.app_chart_url.call(null,new cljs.core.Keyword(null,"current-app","current-app",1533042174).cljs$core$IFn$_invoke$arity$1(self__.app),new cljs.core.Keyword(null,"ms-per-req","ms-per-req",-493938993))], null)], null)))),React.DOM.div({"className": "col-md-4"},React.DOM.h3(null,"Requests per Minute"),sablono.interpreter.interpret.call(null,om.core.build.call(null,tamarack.components.chart.component,self__.app,new cljs.core.PersistentArrayMap(null, 1, [new cljs.core.Keyword(null,"opts","opts",155075701),new cljs.core.PersistentArrayMap(null, 1, [new cljs.core.Keyword(null,"data-url","data-url",-1627669834),tamarack.pages.app_dashboard.app_chart_url.call(null,new cljs.core.Keyword(null,"current-app","current-app",1533042174).cljs$core$IFn$_invoke$arity$1(self__.app),new cljs.core.Keyword(null,"reqs-per-min","reqs-per-min",687617032))], null)], null)))),React.DOM.div({"className": "col-md-4"},React.DOM.h3(null,"Errors per Request"),sablono.interpreter.interpret.call(null,om.core.build.call(null,tamarack.components.chart.component,self__.app,new cljs.core.PersistentArrayMap(null, 1, [new cljs.core.Keyword(null,"opts","opts",155075701),new cljs.core.PersistentArrayMap(null, 1, [new cljs.core.Keyword(null,"data-url","data-url",-1627669834),tamarack.pages.app_dashboard.app_chart_url.call(null,new cljs.core.Keyword(null,"current-app","current-app",1533042174).cljs$core$IFn$_invoke$arity$1(self__.app),new cljs.core.Keyword(null,"errs-per-req","errs-per-req",929944958))], null)], null))))),React.DOM.div({"className": "row"},React.DOM.div({"className": "col-md-4"},React.DOM.h3(null,"Slowest Endpoints"),sablono.interpreter.interpret.call(null,om.core.build.call(null,tamarack.components.agg_table.component,self__.app,new cljs.core.PersistentArrayMap(null, 1, [new cljs.core.Keyword(null,"opts","opts",155075701),new cljs.core.PersistentArrayMap(null, 3, [new cljs.core.Keyword(null,"agg-type","agg-type",1621538561),new cljs.core.Keyword(null,"ms-per-req","ms-per-req",-493938993),new cljs.core.Keyword(null,"round-fn","round-fn",-1368487407),cljs.core.partial.call(null,tamarack.util.round_to,(2)),new cljs.core.Keyword(null,"unit","unit",375175175)," ms"], null)], null)))),React.DOM.div({"className": "col-md-4"},React.DOM.h3(null,"Most Requested Endpoints"),sablono.interpreter.interpret.call(null,om.core.build.call(null,tamarack.components.agg_table.component,self__.app,new cljs.core.PersistentArrayMap(null, 1, [new cljs.core.Keyword(null,"opts","opts",155075701),new cljs.core.PersistentArrayMap(null, 3, [new cljs.core.Keyword(null,"agg-type","agg-type",1621538561),new cljs.core.Keyword(null,"reqs-per-min","reqs-per-min",687617032),new cljs.core.Keyword(null,"round-fn","round-fn",-1368487407),cljs.core.partial.call(null,tamarack.util.round_to,(2)),new cljs.core.Keyword(null,"unit","unit",375175175)," rpm"], null)], null)))),React.DOM.div({"className": "col-md-4"},React.DOM.h3(null,"Endpoints Taking Most Time"),sablono.interpreter.interpret.call(null,om.core.build.call(null,tamarack.components.agg_table.component,self__.app,new cljs.core.PersistentArrayMap(null, 1, [new cljs.core.Keyword(null,"opts","opts",155075701),new cljs.core.PersistentArrayMap(null, 3, [new cljs.core.Keyword(null,"agg-type","agg-type",1621538561),new cljs.core.Keyword(null,"total-time","total-time",-1657781641),new cljs.core.Keyword(null,"round-fn","round-fn",-1368487407),cljs.core.partial.call(null,tamarack.util.round_to,(2)),new cljs.core.Keyword(null,"unit","unit",375175175)," ms"], null)], null))))))));
});
tamarack.pages.app_dashboard.t7239.prototype.om$core$IDisplayName$ = true;
tamarack.pages.app_dashboard.t7239.prototype.om$core$IDisplayName$display_name$arity$1 = (function (_){var self__ = this;
var ___$1 = this;return "AppDashboard";
});
tamarack.pages.app_dashboard.t7239.prototype.cljs$core$IMeta$_meta$arity$1 = (function (_7241){var self__ = this;
var _7241__$1 = this;return self__.meta7240;
});
tamarack.pages.app_dashboard.t7239.prototype.cljs$core$IWithMeta$_with_meta$arity$2 = (function (_7241,meta7240__$1){var self__ = this;
var _7241__$1 = this;return (new tamarack.pages.app_dashboard.t7239(self__.owner,self__.app,self__.page,meta7240__$1));
});
tamarack.pages.app_dashboard.__GT_t7239 = (function __GT_t7239(owner__$1,app__$1,page__$1,meta7240){return (new tamarack.pages.app_dashboard.t7239(owner__$1,app__$1,page__$1,meta7240));
});
}
return (new tamarack.pages.app_dashboard.t7239(owner,app,page,null));
});

//# sourceMappingURL=app_dashboard.js.map