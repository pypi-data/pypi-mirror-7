// Compiled by ClojureScript 0.0-2234
goog.provide('tamarack.pages.main');
goog.require('cljs.core');
goog.require('tamarack.pages.all_apps');
goog.require('tamarack.pages.app_endpoint_overview');
goog.require('tamarack.pages.app_endpoint_overview');
goog.require('tamarack.pages.all_apps');
goog.require('sablono.core');
goog.require('tamarack.state');
goog.require('sablono.core');
goog.require('tamarack.state');
goog.require('tamarack.pages.app_dashboard');
goog.require('om.core');
goog.require('om.core');
goog.require('tamarack.pages.app_dashboard');
tamarack.pages.main.page = (function page(app,owner){if(typeof tamarack.pages.main.t7245 !== 'undefined')
{} else
{
/**
* @constructor
*/
tamarack.pages.main.t7245 = (function (owner,app,page,meta7246){
this.owner = owner;
this.app = app;
this.page = page;
this.meta7246 = meta7246;
this.cljs$lang$protocol_mask$partition1$ = 0;
this.cljs$lang$protocol_mask$partition0$ = 393216;
})
tamarack.pages.main.t7245.cljs$lang$type = true;
tamarack.pages.main.t7245.cljs$lang$ctorStr = "tamarack.pages.main/t7245";
tamarack.pages.main.t7245.cljs$lang$ctorPrWriter = (function (this__4140__auto__,writer__4141__auto__,opt__4142__auto__){return cljs.core._write(writer__4141__auto__,"tamarack.pages.main/t7245");
});
tamarack.pages.main.t7245.prototype.om$core$IRender$ = true;
tamarack.pages.main.t7245.prototype.om$core$IRender$render$arity$1 = (function (_){var self__ = this;
var ___$1 = this;var pred__7248 = cljs.core._EQ_;var expr__7249 = cljs.core.constant$keyword$112.cljs$core$IFn$_invoke$arity$1(self__.app);if(cljs.core.truth_((pred__7248.cljs$core$IFn$_invoke$arity$2 ? pred__7248.cljs$core$IFn$_invoke$arity$2(cljs.core.constant$keyword$117,expr__7249) : pred__7248.call(null,cljs.core.constant$keyword$117,expr__7249))))
{return om.core.build.cljs$core$IFn$_invoke$arity$2(tamarack.pages.app_endpoint_overview.page,self__.app);
} else
{if(cljs.core.truth_((pred__7248.cljs$core$IFn$_invoke$arity$2 ? pred__7248.cljs$core$IFn$_invoke$arity$2(cljs.core.constant$keyword$114,expr__7249) : pred__7248.call(null,cljs.core.constant$keyword$114,expr__7249))))
{return om.core.build.cljs$core$IFn$_invoke$arity$2(tamarack.pages.app_dashboard.page,self__.app);
} else
{if(cljs.core.truth_((pred__7248.cljs$core$IFn$_invoke$arity$2 ? pred__7248.cljs$core$IFn$_invoke$arity$2(cljs.core.constant$keyword$113,expr__7249) : pred__7248.call(null,cljs.core.constant$keyword$113,expr__7249))))
{return om.core.build.cljs$core$IFn$_invoke$arity$2(tamarack.pages.all_apps.page,self__.app);
} else
{throw (new Error(("No matching clause: "+cljs.core.str.cljs$core$IFn$_invoke$arity$1(expr__7249))));
}
}
}
});
tamarack.pages.main.t7245.prototype.om$core$IWillMount$ = true;
tamarack.pages.main.t7245.prototype.om$core$IWillMount$will_mount$arity$1 = (function (_){var self__ = this;
var ___$1 = this;return window.setInterval(cljs.core.partial.cljs$core$IFn$_invoke$arity$2(tamarack.state.update_timeslice,cljs.core.constant$keyword$100.cljs$core$IFn$_invoke$arity$1(self__.app)),1000);
});
tamarack.pages.main.t7245.prototype.om$core$IDisplayName$ = true;
tamarack.pages.main.t7245.prototype.om$core$IDisplayName$display_name$arity$1 = (function (_){var self__ = this;
var ___$1 = this;return "Main";
});
tamarack.pages.main.t7245.prototype.cljs$core$IMeta$_meta$arity$1 = (function (_7247){var self__ = this;
var _7247__$1 = this;return self__.meta7246;
});
tamarack.pages.main.t7245.prototype.cljs$core$IWithMeta$_with_meta$arity$2 = (function (_7247,meta7246__$1){var self__ = this;
var _7247__$1 = this;return (new tamarack.pages.main.t7245(self__.owner,self__.app,self__.page,meta7246__$1));
});
tamarack.pages.main.__GT_t7245 = (function __GT_t7245(owner__$1,app__$1,page__$1,meta7246){return (new tamarack.pages.main.t7245(owner__$1,app__$1,page__$1,meta7246));
});
}
return (new tamarack.pages.main.t7245(owner,app,page,null));
});
