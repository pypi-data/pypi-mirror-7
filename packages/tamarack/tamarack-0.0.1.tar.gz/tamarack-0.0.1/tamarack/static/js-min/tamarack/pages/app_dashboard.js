// Compiled by ClojureScript 0.0-2234
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
goog.require('tamarack.components.app_navbar');
goog.require('tamarack.components.chart');
goog.require('clojure.string');
goog.require('tamarack.components.app_navbar');
goog.require('tamarack.components.chart');
tamarack.pages.app_dashboard.app_chart_url = (function app_chart_url(app,chart_type){var comps = new cljs.core.PersistentVector(null, 4, 5, cljs.core.PersistentVector.EMPTY_NODE, ["/explorer-api/v1/applications",cljs.core.constant$keyword$99.cljs$core$IFn$_invoke$arity$1(app),"chart",cljs.core.subs.cljs$core$IFn$_invoke$arity$2((''+cljs.core.str.cljs$core$IFn$_invoke$arity$1(chart_type)),1)], null);return clojure.string.join.cljs$core$IFn$_invoke$arity$2("/",comps);
});
tamarack.pages.app_dashboard.page = (function page(app,owner){if(typeof tamarack.pages.app_dashboard.t7203 !== 'undefined')
{} else
{
/**
* @constructor
*/
tamarack.pages.app_dashboard.t7203 = (function (owner,app,page,meta7204){
this.owner = owner;
this.app = app;
this.page = page;
this.meta7204 = meta7204;
this.cljs$lang$protocol_mask$partition1$ = 0;
this.cljs$lang$protocol_mask$partition0$ = 393216;
})
tamarack.pages.app_dashboard.t7203.cljs$lang$type = true;
tamarack.pages.app_dashboard.t7203.cljs$lang$ctorStr = "tamarack.pages.app-dashboard/t7203";
tamarack.pages.app_dashboard.t7203.cljs$lang$ctorPrWriter = (function (this__4140__auto__,writer__4141__auto__,opt__4142__auto__){return cljs.core._write(writer__4141__auto__,"tamarack.pages.app-dashboard/t7203");
});
tamarack.pages.app_dashboard.t7203.prototype.om$core$IRender$ = true;
tamarack.pages.app_dashboard.t7203.prototype.om$core$IRender$render$arity$1 = (function (_){var self__ = this;
var ___$1 = this;return React.DOM.div({"className": "app-dashboard"},React.DOM.div({"className": "row"},React.DOM.div({"className": "col-md-12"},React.DOM.h2(null,"Application Overview for ",sablono.interpreter.interpret(cljs.core.constant$keyword$123.cljs$core$IFn$_invoke$arity$1(cljs.core.constant$keyword$98.cljs$core$IFn$_invoke$arity$1(self__.app)))))),React.DOM.div({"className": "row"},React.DOM.div({"className": "col-md-9"},React.DOM.div({"className": "row"},React.DOM.div({"className": "col-md-4"},React.DOM.h3(null,"Time per Request"),sablono.interpreter.interpret(om.core.build.cljs$core$IFn$_invoke$arity$3(tamarack.components.chart.component,self__.app,new cljs.core.PersistentArrayMap(null, 1, [cljs.core.constant$keyword$90,new cljs.core.PersistentArrayMap(null, 1, [cljs.core.constant$keyword$125,tamarack.pages.app_dashboard.app_chart_url(cljs.core.constant$keyword$98.cljs$core$IFn$_invoke$arity$1(self__.app),cljs.core.constant$keyword$131)], null)], null)))),React.DOM.div({"className": "col-md-4"},React.DOM.h3(null,"Requests per Minute"),sablono.interpreter.interpret(om.core.build.cljs$core$IFn$_invoke$arity$3(tamarack.components.chart.component,self__.app,new cljs.core.PersistentArrayMap(null, 1, [cljs.core.constant$keyword$90,new cljs.core.PersistentArrayMap(null, 1, [cljs.core.constant$keyword$125,tamarack.pages.app_dashboard.app_chart_url(cljs.core.constant$keyword$98.cljs$core$IFn$_invoke$arity$1(self__.app),cljs.core.constant$keyword$132)], null)], null)))),React.DOM.div({"className": "col-md-4"},React.DOM.h3(null,"Errors per Request"),sablono.interpreter.interpret(om.core.build.cljs$core$IFn$_invoke$arity$3(tamarack.components.chart.component,self__.app,new cljs.core.PersistentArrayMap(null, 1, [cljs.core.constant$keyword$90,new cljs.core.PersistentArrayMap(null, 1, [cljs.core.constant$keyword$125,tamarack.pages.app_dashboard.app_chart_url(cljs.core.constant$keyword$98.cljs$core$IFn$_invoke$arity$1(self__.app),cljs.core.constant$keyword$133)], null)], null))))),React.DOM.div({"className": "row"},React.DOM.div({"className": "col-md-4"},React.DOM.h3(null,"Slowest Endpoints"),sablono.interpreter.interpret(om.core.build.cljs$core$IFn$_invoke$arity$3(tamarack.components.agg_table.component,self__.app,new cljs.core.PersistentArrayMap(null, 1, [cljs.core.constant$keyword$90,new cljs.core.PersistentArrayMap(null, 3, [cljs.core.constant$keyword$120,cljs.core.constant$keyword$131,cljs.core.constant$keyword$119,cljs.core.partial.cljs$core$IFn$_invoke$arity$2(tamarack.util.round_to,2),cljs.core.constant$keyword$118," ms"], null)], null)))),React.DOM.div({"className": "col-md-4"},React.DOM.h3(null,"Most Requested Endpoints"),sablono.interpreter.interpret(om.core.build.cljs$core$IFn$_invoke$arity$3(tamarack.components.agg_table.component,self__.app,new cljs.core.PersistentArrayMap(null, 1, [cljs.core.constant$keyword$90,new cljs.core.PersistentArrayMap(null, 3, [cljs.core.constant$keyword$120,cljs.core.constant$keyword$132,cljs.core.constant$keyword$119,cljs.core.partial.cljs$core$IFn$_invoke$arity$2(tamarack.util.round_to,2),cljs.core.constant$keyword$118," rpm"], null)], null)))),React.DOM.div({"className": "col-md-4"},React.DOM.h3(null,"Endpoints Taking Most Time"),sablono.interpreter.interpret(om.core.build.cljs$core$IFn$_invoke$arity$3(tamarack.components.agg_table.component,self__.app,new cljs.core.PersistentArrayMap(null, 1, [cljs.core.constant$keyword$90,new cljs.core.PersistentArrayMap(null, 3, [cljs.core.constant$keyword$120,cljs.core.constant$keyword$134,cljs.core.constant$keyword$119,cljs.core.partial.cljs$core$IFn$_invoke$arity$2(tamarack.util.round_to,2),cljs.core.constant$keyword$118," ms"], null)], null)))))),(function (){var attrs7218 = om.core.build.cljs$core$IFn$_invoke$arity$2(tamarack.components.app_navbar.component,self__.app);return cljs.core.apply.cljs$core$IFn$_invoke$arity$3(React.DOM.div,((cljs.core.map_QMARK_(attrs7218))?sablono.interpreter.attributes(sablono.util.merge_with_class.cljs$core$IFn$_invoke$arity$variadic(cljs.core.array_seq([new cljs.core.PersistentArrayMap(null, 1, [cljs.core.constant$keyword$28,new cljs.core.PersistentVector(null, 1, 5, cljs.core.PersistentVector.EMPTY_NODE, ["col-md-3"], null)], null),attrs7218], 0))):{"className": "col-md-3"}),cljs.core.remove(cljs.core.nil_QMARK_,((cljs.core.map_QMARK_(attrs7218))?cljs.core.PersistentVector.EMPTY:new cljs.core.PersistentVector(null, 1, 5, cljs.core.PersistentVector.EMPTY_NODE, [sablono.interpreter.interpret(attrs7218)], null))));
})()));
});
tamarack.pages.app_dashboard.t7203.prototype.om$core$IDisplayName$ = true;
tamarack.pages.app_dashboard.t7203.prototype.om$core$IDisplayName$display_name$arity$1 = (function (_){var self__ = this;
var ___$1 = this;return "AppDashboard";
});
tamarack.pages.app_dashboard.t7203.prototype.cljs$core$IMeta$_meta$arity$1 = (function (_7205){var self__ = this;
var _7205__$1 = this;return self__.meta7204;
});
tamarack.pages.app_dashboard.t7203.prototype.cljs$core$IWithMeta$_with_meta$arity$2 = (function (_7205,meta7204__$1){var self__ = this;
var _7205__$1 = this;return (new tamarack.pages.app_dashboard.t7203(self__.owner,self__.app,self__.page,meta7204__$1));
});
tamarack.pages.app_dashboard.__GT_t7203 = (function __GT_t7203(owner__$1,app__$1,page__$1,meta7204){return (new tamarack.pages.app_dashboard.t7203(owner__$1,app__$1,page__$1,meta7204));
});
}
return (new tamarack.pages.app_dashboard.t7203(owner,app,page,null));
});
