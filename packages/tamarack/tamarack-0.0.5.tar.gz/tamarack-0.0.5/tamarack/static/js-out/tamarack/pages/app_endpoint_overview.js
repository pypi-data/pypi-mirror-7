// Compiled by ClojureScript 0.0-2268
goog.provide('tamarack.pages.app_endpoint_overview');
goog.require('cljs.core');
goog.require('tamarack.components.chart');
goog.require('tamarack.components.chart');
goog.require('clojure.string');
goog.require('clojure.string');
goog.require('sablono.core');
goog.require('sablono.core');
goog.require('om.core');
goog.require('om.core');
tamarack.pages.app_endpoint_overview.app_endpoint_chart_url = (function app_endpoint_chart_url(app,endpoint,chart_type){var comps = new cljs.core.PersistentVector(null, 6, 5, cljs.core.PersistentVector.EMPTY_NODE, ["/explorer-api/v1/applications",new cljs.core.Keyword(null,"name","name",1843675177).cljs$core$IFn$_invoke$arity$1(app),"endpoints",endpoint,"chart",cljs.core.subs.call(null,(''+cljs.core.str.cljs$core$IFn$_invoke$arity$1(chart_type)),(1))], null);return clojure.string.join.call(null,"/",comps);
});
tamarack.pages.app_endpoint_overview.page = (function page(app,owner){if(typeof tamarack.pages.app_endpoint_overview.t7263 !== 'undefined')
{} else
{
/**
* @constructor
*/
tamarack.pages.app_endpoint_overview.t7263 = (function (owner,app,page,meta7264){
this.owner = owner;
this.app = app;
this.page = page;
this.meta7264 = meta7264;
this.cljs$lang$protocol_mask$partition1$ = 0;
this.cljs$lang$protocol_mask$partition0$ = 393216;
})
tamarack.pages.app_endpoint_overview.t7263.cljs$lang$type = true;
tamarack.pages.app_endpoint_overview.t7263.cljs$lang$ctorStr = "tamarack.pages.app-endpoint-overview/t7263";
tamarack.pages.app_endpoint_overview.t7263.cljs$lang$ctorPrWriter = (function (this__4145__auto__,writer__4146__auto__,opt__4147__auto__){return cljs.core._write.call(null,writer__4146__auto__,"tamarack.pages.app-endpoint-overview/t7263");
});
tamarack.pages.app_endpoint_overview.t7263.prototype.om$core$IRender$ = true;
tamarack.pages.app_endpoint_overview.t7263.prototype.om$core$IRender$render$arity$1 = (function (_){var self__ = this;
var ___$1 = this;return React.DOM.div({"className": "app-endpoint-overview"},React.DOM.div({"className": "row"},React.DOM.div({"className": "col-md-12"},React.DOM.h2(null,"Endpoint Overiew for \"",sablono.interpreter.interpret.call(null,new cljs.core.Keyword(null,"current-endpoint","current-endpoint",-28327621).cljs$core$IFn$_invoke$arity$1(self__.app)),"\""))),React.DOM.div({"className": "row"},React.DOM.div({"className": "col-md-9"},React.DOM.div({"className": "row"},React.DOM.div({"className": "col-md-4"},React.DOM.h3(null,"Time per Request"),sablono.interpreter.interpret.call(null,om.core.build.call(null,tamarack.components.chart.component,self__.app,new cljs.core.PersistentArrayMap(null, 1, [new cljs.core.Keyword(null,"opts","opts",155075701),new cljs.core.PersistentArrayMap(null, 1, [new cljs.core.Keyword(null,"data-url","data-url",-1627669834),tamarack.pages.app_endpoint_overview.app_endpoint_chart_url.call(null,new cljs.core.Keyword(null,"current-app","current-app",1533042174).cljs$core$IFn$_invoke$arity$1(self__.app),new cljs.core.Keyword(null,"current-endpoint","current-endpoint",-28327621).cljs$core$IFn$_invoke$arity$1(self__.app),new cljs.core.Keyword(null,"ms-per-req","ms-per-req",-493938993))], null)], null)))),React.DOM.div({"className": "col-md-4"},React.DOM.h3(null,"Requests per Minute"),sablono.interpreter.interpret.call(null,om.core.build.call(null,tamarack.components.chart.component,self__.app,new cljs.core.PersistentArrayMap(null, 1, [new cljs.core.Keyword(null,"opts","opts",155075701),new cljs.core.PersistentArrayMap(null, 1, [new cljs.core.Keyword(null,"data-url","data-url",-1627669834),tamarack.pages.app_endpoint_overview.app_endpoint_chart_url.call(null,new cljs.core.Keyword(null,"current-app","current-app",1533042174).cljs$core$IFn$_invoke$arity$1(self__.app),new cljs.core.Keyword(null,"current-endpoint","current-endpoint",-28327621).cljs$core$IFn$_invoke$arity$1(self__.app),new cljs.core.Keyword(null,"reqs-per-min","reqs-per-min",687617032))], null)], null)))),React.DOM.div({"className": "col-md-4"},React.DOM.h3(null,"Errors per Request"),sablono.interpreter.interpret.call(null,om.core.build.call(null,tamarack.components.chart.component,self__.app,new cljs.core.PersistentArrayMap(null, 1, [new cljs.core.Keyword(null,"opts","opts",155075701),new cljs.core.PersistentArrayMap(null, 1, [new cljs.core.Keyword(null,"data-url","data-url",-1627669834),tamarack.pages.app_endpoint_overview.app_endpoint_chart_url.call(null,new cljs.core.Keyword(null,"current-app","current-app",1533042174).cljs$core$IFn$_invoke$arity$1(self__.app),new cljs.core.Keyword(null,"current-endpoint","current-endpoint",-28327621).cljs$core$IFn$_invoke$arity$1(self__.app),new cljs.core.Keyword(null,"errs-per-req","errs-per-req",929944958))], null)], null))))))));
});
tamarack.pages.app_endpoint_overview.t7263.prototype.om$core$IDisplayName$ = true;
tamarack.pages.app_endpoint_overview.t7263.prototype.om$core$IDisplayName$display_name$arity$1 = (function (_){var self__ = this;
var ___$1 = this;return "AppEndpointOverview";
});
tamarack.pages.app_endpoint_overview.t7263.prototype.cljs$core$IMeta$_meta$arity$1 = (function (_7265){var self__ = this;
var _7265__$1 = this;return self__.meta7264;
});
tamarack.pages.app_endpoint_overview.t7263.prototype.cljs$core$IWithMeta$_with_meta$arity$2 = (function (_7265,meta7264__$1){var self__ = this;
var _7265__$1 = this;return (new tamarack.pages.app_endpoint_overview.t7263(self__.owner,self__.app,self__.page,meta7264__$1));
});
tamarack.pages.app_endpoint_overview.__GT_t7263 = (function __GT_t7263(owner__$1,app__$1,page__$1,meta7264){return (new tamarack.pages.app_endpoint_overview.t7263(owner__$1,app__$1,page__$1,meta7264));
});
}
return (new tamarack.pages.app_endpoint_overview.t7263(owner,app,page,null));
});

//# sourceMappingURL=app_endpoint_overview.js.map