
(function(l, r) { if (!l || l.getElementById('livereloadscript')) return; r = l.createElement('script'); r.async = 1; r.src = '//' + (self.location.host || 'localhost').split(':')[0] + ':35729/livereload.js?snipver=1'; r.id = 'livereloadscript'; l.getElementsByTagName('head')[0].appendChild(r) })(self.document);
var app = (function () {
    'use strict';

    function noop() { }
    function assign(tar, src) {
        // @ts-ignore
        for (const k in src)
            tar[k] = src[k];
        return tar;
    }
    function add_location(element, file, line, column, char) {
        element.__svelte_meta = {
            loc: { file, line, column, char }
        };
    }
    function run(fn) {
        return fn();
    }
    function blank_object() {
        return Object.create(null);
    }
    function run_all(fns) {
        fns.forEach(run);
    }
    function is_function(thing) {
        return typeof thing === 'function';
    }
    function safe_not_equal(a, b) {
        return a != a ? b == b : a !== b || ((a && typeof a === 'object') || typeof a === 'function');
    }
    let src_url_equal_anchor;
    function src_url_equal(element_src, url) {
        if (!src_url_equal_anchor) {
            src_url_equal_anchor = document.createElement('a');
        }
        src_url_equal_anchor.href = url;
        return element_src === src_url_equal_anchor.href;
    }
    function is_empty(obj) {
        return Object.keys(obj).length === 0;
    }
    function exclude_internal_props(props) {
        const result = {};
        for (const k in props)
            if (k[0] !== '$')
                result[k] = props[k];
        return result;
    }
    function compute_rest_props(props, keys) {
        const rest = {};
        keys = new Set(keys);
        for (const k in props)
            if (!keys.has(k) && k[0] !== '$')
                rest[k] = props[k];
        return rest;
    }
    function append(target, node) {
        target.appendChild(node);
    }
    function insert(target, node, anchor) {
        target.insertBefore(node, anchor || null);
    }
    function detach(node) {
        if (node.parentNode) {
            node.parentNode.removeChild(node);
        }
    }
    function destroy_each(iterations, detaching) {
        for (let i = 0; i < iterations.length; i += 1) {
            if (iterations[i])
                iterations[i].d(detaching);
        }
    }
    function element(name) {
        return document.createElement(name);
    }
    function svg_element(name) {
        return document.createElementNS('http://www.w3.org/2000/svg', name);
    }
    function text(data) {
        return document.createTextNode(data);
    }
    function space() {
        return text(' ');
    }
    function empty() {
        return text('');
    }
    function attr(node, attribute, value) {
        if (value == null)
            node.removeAttribute(attribute);
        else if (node.getAttribute(attribute) !== value)
            node.setAttribute(attribute, value);
    }
    function set_svg_attributes(node, attributes) {
        for (const key in attributes) {
            attr(node, key, attributes[key]);
        }
    }
    function children(element) {
        return Array.from(element.childNodes);
    }
    function custom_event(type, detail, { bubbles = false, cancelable = false } = {}) {
        const e = document.createEvent('CustomEvent');
        e.initCustomEvent(type, bubbles, cancelable, detail);
        return e;
    }

    let current_component;
    function set_current_component(component) {
        current_component = component;
    }

    const dirty_components = [];
    const binding_callbacks = [];
    const render_callbacks = [];
    const flush_callbacks = [];
    const resolved_promise = Promise.resolve();
    let update_scheduled = false;
    function schedule_update() {
        if (!update_scheduled) {
            update_scheduled = true;
            resolved_promise.then(flush);
        }
    }
    function add_render_callback(fn) {
        render_callbacks.push(fn);
    }
    // flush() calls callbacks in this order:
    // 1. All beforeUpdate callbacks, in order: parents before children
    // 2. All bind:this callbacks, in reverse order: children before parents.
    // 3. All afterUpdate callbacks, in order: parents before children. EXCEPT
    //    for afterUpdates called during the initial onMount, which are called in
    //    reverse order: children before parents.
    // Since callbacks might update component values, which could trigger another
    // call to flush(), the following steps guard against this:
    // 1. During beforeUpdate, any updated components will be added to the
    //    dirty_components array and will cause a reentrant call to flush(). Because
    //    the flush index is kept outside the function, the reentrant call will pick
    //    up where the earlier call left off and go through all dirty components. The
    //    current_component value is saved and restored so that the reentrant call will
    //    not interfere with the "parent" flush() call.
    // 2. bind:this callbacks cannot trigger new flush() calls.
    // 3. During afterUpdate, any updated components will NOT have their afterUpdate
    //    callback called a second time; the seen_callbacks set, outside the flush()
    //    function, guarantees this behavior.
    const seen_callbacks = new Set();
    let flushidx = 0; // Do *not* move this inside the flush() function
    function flush() {
        // Do not reenter flush while dirty components are updated, as this can
        // result in an infinite loop. Instead, let the inner flush handle it.
        // Reentrancy is ok afterwards for bindings etc.
        if (flushidx !== 0) {
            return;
        }
        const saved_component = current_component;
        do {
            // first, call beforeUpdate functions
            // and update components
            try {
                while (flushidx < dirty_components.length) {
                    const component = dirty_components[flushidx];
                    flushidx++;
                    set_current_component(component);
                    update(component.$$);
                }
            }
            catch (e) {
                // reset dirty state to not end up in a deadlocked state and then rethrow
                dirty_components.length = 0;
                flushidx = 0;
                throw e;
            }
            set_current_component(null);
            dirty_components.length = 0;
            flushidx = 0;
            while (binding_callbacks.length)
                binding_callbacks.pop()();
            // then, once components are updated, call
            // afterUpdate functions. This may cause
            // subsequent updates...
            for (let i = 0; i < render_callbacks.length; i += 1) {
                const callback = render_callbacks[i];
                if (!seen_callbacks.has(callback)) {
                    // ...so guard against infinite loops
                    seen_callbacks.add(callback);
                    callback();
                }
            }
            render_callbacks.length = 0;
        } while (dirty_components.length);
        while (flush_callbacks.length) {
            flush_callbacks.pop()();
        }
        update_scheduled = false;
        seen_callbacks.clear();
        set_current_component(saved_component);
    }
    function update($$) {
        if ($$.fragment !== null) {
            $$.update();
            run_all($$.before_update);
            const dirty = $$.dirty;
            $$.dirty = [-1];
            $$.fragment && $$.fragment.p($$.ctx, dirty);
            $$.after_update.forEach(add_render_callback);
        }
    }
    const outroing = new Set();
    let outros;
    function transition_in(block, local) {
        if (block && block.i) {
            outroing.delete(block);
            block.i(local);
        }
    }
    function transition_out(block, local, detach, callback) {
        if (block && block.o) {
            if (outroing.has(block))
                return;
            outroing.add(block);
            outros.c.push(() => {
                outroing.delete(block);
                if (callback) {
                    if (detach)
                        block.d(1);
                    callback();
                }
            });
            block.o(local);
        }
        else if (callback) {
            callback();
        }
    }

    function get_spread_update(levels, updates) {
        const update = {};
        const to_null_out = {};
        const accounted_for = { $$scope: 1 };
        let i = levels.length;
        while (i--) {
            const o = levels[i];
            const n = updates[i];
            if (n) {
                for (const key in o) {
                    if (!(key in n))
                        to_null_out[key] = 1;
                }
                for (const key in n) {
                    if (!accounted_for[key]) {
                        update[key] = n[key];
                        accounted_for[key] = 1;
                    }
                }
                levels[i] = n;
            }
            else {
                for (const key in o) {
                    accounted_for[key] = 1;
                }
            }
        }
        for (const key in to_null_out) {
            if (!(key in update))
                update[key] = undefined;
        }
        return update;
    }
    function create_component(block) {
        block && block.c();
    }
    function mount_component(component, target, anchor, customElement) {
        const { fragment, after_update } = component.$$;
        fragment && fragment.m(target, anchor);
        if (!customElement) {
            // onMount happens before the initial afterUpdate
            add_render_callback(() => {
                const new_on_destroy = component.$$.on_mount.map(run).filter(is_function);
                // if the component was destroyed immediately
                // it will update the `$$.on_destroy` reference to `null`.
                // the destructured on_destroy may still reference to the old array
                if (component.$$.on_destroy) {
                    component.$$.on_destroy.push(...new_on_destroy);
                }
                else {
                    // Edge case - component was destroyed immediately,
                    // most likely as a result of a binding initialising
                    run_all(new_on_destroy);
                }
                component.$$.on_mount = [];
            });
        }
        after_update.forEach(add_render_callback);
    }
    function destroy_component(component, detaching) {
        const $$ = component.$$;
        if ($$.fragment !== null) {
            run_all($$.on_destroy);
            $$.fragment && $$.fragment.d(detaching);
            // TODO null out other refs, including component.$$ (but need to
            // preserve final state?)
            $$.on_destroy = $$.fragment = null;
            $$.ctx = [];
        }
    }
    function make_dirty(component, i) {
        if (component.$$.dirty[0] === -1) {
            dirty_components.push(component);
            schedule_update();
            component.$$.dirty.fill(0);
        }
        component.$$.dirty[(i / 31) | 0] |= (1 << (i % 31));
    }
    function init(component, options, instance, create_fragment, not_equal, props, append_styles, dirty = [-1]) {
        const parent_component = current_component;
        set_current_component(component);
        const $$ = component.$$ = {
            fragment: null,
            ctx: [],
            // state
            props,
            update: noop,
            not_equal,
            bound: blank_object(),
            // lifecycle
            on_mount: [],
            on_destroy: [],
            on_disconnect: [],
            before_update: [],
            after_update: [],
            context: new Map(options.context || (parent_component ? parent_component.$$.context : [])),
            // everything else
            callbacks: blank_object(),
            dirty,
            skip_bound: false,
            root: options.target || parent_component.$$.root
        };
        append_styles && append_styles($$.root);
        let ready = false;
        $$.ctx = instance
            ? instance(component, options.props || {}, (i, ret, ...rest) => {
                const value = rest.length ? rest[0] : ret;
                if ($$.ctx && not_equal($$.ctx[i], $$.ctx[i] = value)) {
                    if (!$$.skip_bound && $$.bound[i])
                        $$.bound[i](value);
                    if (ready)
                        make_dirty(component, i);
                }
                return ret;
            })
            : [];
        $$.update();
        ready = true;
        run_all($$.before_update);
        // `false` as a special case of no DOM component
        $$.fragment = create_fragment ? create_fragment($$.ctx) : false;
        if (options.target) {
            if (options.hydrate) {
                const nodes = children(options.target);
                // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
                $$.fragment && $$.fragment.l(nodes);
                nodes.forEach(detach);
            }
            else {
                // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
                $$.fragment && $$.fragment.c();
            }
            if (options.intro)
                transition_in(component.$$.fragment);
            mount_component(component, options.target, options.anchor, options.customElement);
            flush();
        }
        set_current_component(parent_component);
    }
    /**
     * Base class for Svelte components. Used when dev=false.
     */
    class SvelteComponent {
        $destroy() {
            destroy_component(this, 1);
            this.$destroy = noop;
        }
        $on(type, callback) {
            if (!is_function(callback)) {
                return noop;
            }
            const callbacks = (this.$$.callbacks[type] || (this.$$.callbacks[type] = []));
            callbacks.push(callback);
            return () => {
                const index = callbacks.indexOf(callback);
                if (index !== -1)
                    callbacks.splice(index, 1);
            };
        }
        $set($$props) {
            if (this.$$set && !is_empty($$props)) {
                this.$$.skip_bound = true;
                this.$$set($$props);
                this.$$.skip_bound = false;
            }
        }
    }

    function dispatch_dev(type, detail) {
        document.dispatchEvent(custom_event(type, Object.assign({ version: '3.55.1' }, detail), { bubbles: true }));
    }
    function append_dev(target, node) {
        dispatch_dev('SvelteDOMInsert', { target, node });
        append(target, node);
    }
    function insert_dev(target, node, anchor) {
        dispatch_dev('SvelteDOMInsert', { target, node, anchor });
        insert(target, node, anchor);
    }
    function detach_dev(node) {
        dispatch_dev('SvelteDOMRemove', { node });
        detach(node);
    }
    function attr_dev(node, attribute, value) {
        attr(node, attribute, value);
        if (value == null)
            dispatch_dev('SvelteDOMRemoveAttribute', { node, attribute });
        else
            dispatch_dev('SvelteDOMSetAttribute', { node, attribute, value });
    }
    function validate_each_argument(arg) {
        if (typeof arg !== 'string' && !(arg && typeof arg === 'object' && 'length' in arg)) {
            let msg = '{#each} only iterates over array-like objects.';
            if (typeof Symbol === 'function' && arg && Symbol.iterator in arg) {
                msg += ' You can use a spread to convert this iterable into an array.';
            }
            throw new Error(msg);
        }
    }
    function validate_slots(name, slot, keys) {
        for (const slot_key of Object.keys(slot)) {
            if (!~keys.indexOf(slot_key)) {
                console.warn(`<${name}> received an unexpected slot "${slot_key}".`);
            }
        }
    }
    /**
     * Base class for Svelte components with some minor dev-enhancements. Used when dev=true.
     */
    class SvelteComponentDev extends SvelteComponent {
        constructor(options) {
            if (!options || (!options.target && !options.$$inline)) {
                throw new Error("'target' is a required option");
            }
            super();
        }
        $destroy() {
            super.$destroy();
            this.$destroy = () => {
                console.warn('Component was already destroyed'); // eslint-disable-line no-console
            };
        }
        $capture_state() { }
        $inject_state() { }
    }

    /* node_modules\@steeze-ui\svelte-icon\Icon.svelte generated by Svelte v3.55.1 */

    const file$3 = "node_modules\\@steeze-ui\\svelte-icon\\Icon.svelte";

    function get_each_context$1(ctx, list, i) {
    	const child_ctx = ctx.slice();
    	child_ctx[5] = list[i];
    	return child_ctx;
    }

    function get_each_context_1(ctx, list, i) {
    	const child_ctx = ctx.slice();
    	child_ctx[5] = list[i];
    	return child_ctx;
    }

    function get_each_context_2(ctx, list, i) {
    	const child_ctx = ctx.slice();
    	child_ctx[5] = list[i];
    	return child_ctx;
    }

    function get_each_context_3(ctx, list, i) {
    	const child_ctx = ctx.slice();
    	child_ctx[5] = list[i];
    	return child_ctx;
    }

    function get_each_context_4(ctx, list, i) {
    	const child_ctx = ctx.slice();
    	child_ctx[5] = list[i];
    	return child_ctx;
    }

    function get_each_context_5(ctx, list, i) {
    	const child_ctx = ctx.slice();
    	child_ctx[5] = list[i];
    	return child_ctx;
    }

    // (18:1) {#each icon?.path ?? [] as a}
    function create_each_block_5(ctx) {
    	let path;
    	let path_levels = [/*a*/ ctx[5]];
    	let path_data = {};

    	for (let i = 0; i < path_levels.length; i += 1) {
    		path_data = assign(path_data, path_levels[i]);
    	}

    	const block = {
    		c: function create() {
    			path = svg_element("path");
    			set_svg_attributes(path, path_data);
    			add_location(path, file$3, 18, 2, 507);
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, path, anchor);
    		},
    		p: function update(ctx, dirty) {
    			set_svg_attributes(path, path_data = get_spread_update(path_levels, [dirty & /*icon*/ 2 && /*a*/ ctx[5]]));
    		},
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(path);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_each_block_5.name,
    		type: "each",
    		source: "(18:1) {#each icon?.path ?? [] as a}",
    		ctx
    	});

    	return block;
    }

    // (21:1) {#each icon?.rect ?? [] as a}
    function create_each_block_4(ctx) {
    	let rect;
    	let rect_levels = [/*a*/ ctx[5]];
    	let rect_data = {};

    	for (let i = 0; i < rect_levels.length; i += 1) {
    		rect_data = assign(rect_data, rect_levels[i]);
    	}

    	const block = {
    		c: function create() {
    			rect = svg_element("rect");
    			set_svg_attributes(rect, rect_data);
    			add_location(rect, file$3, 21, 2, 565);
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, rect, anchor);
    		},
    		p: function update(ctx, dirty) {
    			set_svg_attributes(rect, rect_data = get_spread_update(rect_levels, [dirty & /*icon*/ 2 && /*a*/ ctx[5]]));
    		},
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(rect);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_each_block_4.name,
    		type: "each",
    		source: "(21:1) {#each icon?.rect ?? [] as a}",
    		ctx
    	});

    	return block;
    }

    // (24:1) {#each icon?.circle ?? [] as a}
    function create_each_block_3(ctx) {
    	let circle;
    	let circle_levels = [/*a*/ ctx[5]];
    	let circle_data = {};

    	for (let i = 0; i < circle_levels.length; i += 1) {
    		circle_data = assign(circle_data, circle_levels[i]);
    	}

    	const block = {
    		c: function create() {
    			circle = svg_element("circle");
    			set_svg_attributes(circle, circle_data);
    			add_location(circle, file$3, 24, 2, 625);
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, circle, anchor);
    		},
    		p: function update(ctx, dirty) {
    			set_svg_attributes(circle, circle_data = get_spread_update(circle_levels, [dirty & /*icon*/ 2 && /*a*/ ctx[5]]));
    		},
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(circle);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_each_block_3.name,
    		type: "each",
    		source: "(24:1) {#each icon?.circle ?? [] as a}",
    		ctx
    	});

    	return block;
    }

    // (27:1) {#each icon?.polygon ?? [] as a}
    function create_each_block_2(ctx) {
    	let polygon;
    	let polygon_levels = [/*a*/ ctx[5]];
    	let polygon_data = {};

    	for (let i = 0; i < polygon_levels.length; i += 1) {
    		polygon_data = assign(polygon_data, polygon_levels[i]);
    	}

    	const block = {
    		c: function create() {
    			polygon = svg_element("polygon");
    			set_svg_attributes(polygon, polygon_data);
    			add_location(polygon, file$3, 27, 2, 688);
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, polygon, anchor);
    		},
    		p: function update(ctx, dirty) {
    			set_svg_attributes(polygon, polygon_data = get_spread_update(polygon_levels, [dirty & /*icon*/ 2 && /*a*/ ctx[5]]));
    		},
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(polygon);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_each_block_2.name,
    		type: "each",
    		source: "(27:1) {#each icon?.polygon ?? [] as a}",
    		ctx
    	});

    	return block;
    }

    // (30:1) {#each icon?.polyline ?? [] as a}
    function create_each_block_1(ctx) {
    	let polyline;
    	let polyline_levels = [/*a*/ ctx[5]];
    	let polyline_data = {};

    	for (let i = 0; i < polyline_levels.length; i += 1) {
    		polyline_data = assign(polyline_data, polyline_levels[i]);
    	}

    	const block = {
    		c: function create() {
    			polyline = svg_element("polyline");
    			set_svg_attributes(polyline, polyline_data);
    			add_location(polyline, file$3, 30, 2, 753);
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, polyline, anchor);
    		},
    		p: function update(ctx, dirty) {
    			set_svg_attributes(polyline, polyline_data = get_spread_update(polyline_levels, [dirty & /*icon*/ 2 && /*a*/ ctx[5]]));
    		},
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(polyline);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_each_block_1.name,
    		type: "each",
    		source: "(30:1) {#each icon?.polyline ?? [] as a}",
    		ctx
    	});

    	return block;
    }

    // (33:1) {#each icon?.line ?? [] as a}
    function create_each_block$1(ctx) {
    	let line;
    	let line_levels = [/*a*/ ctx[5]];
    	let line_data = {};

    	for (let i = 0; i < line_levels.length; i += 1) {
    		line_data = assign(line_data, line_levels[i]);
    	}

    	const block = {
    		c: function create() {
    			line = svg_element("line");
    			set_svg_attributes(line, line_data);
    			add_location(line, file$3, 33, 2, 815);
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, line, anchor);
    		},
    		p: function update(ctx, dirty) {
    			set_svg_attributes(line, line_data = get_spread_update(line_levels, [dirty & /*icon*/ 2 && /*a*/ ctx[5]]));
    		},
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(line);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_each_block$1.name,
    		type: "each",
    		source: "(33:1) {#each icon?.line ?? [] as a}",
    		ctx
    	});

    	return block;
    }

    function create_fragment$3(ctx) {
    	let svg;
    	let each0_anchor;
    	let each1_anchor;
    	let each2_anchor;
    	let each3_anchor;
    	let each4_anchor;
    	let each_value_5 = /*icon*/ ctx[1]?.path ?? [];
    	validate_each_argument(each_value_5);
    	let each_blocks_5 = [];

    	for (let i = 0; i < each_value_5.length; i += 1) {
    		each_blocks_5[i] = create_each_block_5(get_each_context_5(ctx, each_value_5, i));
    	}

    	let each_value_4 = /*icon*/ ctx[1]?.rect ?? [];
    	validate_each_argument(each_value_4);
    	let each_blocks_4 = [];

    	for (let i = 0; i < each_value_4.length; i += 1) {
    		each_blocks_4[i] = create_each_block_4(get_each_context_4(ctx, each_value_4, i));
    	}

    	let each_value_3 = /*icon*/ ctx[1]?.circle ?? [];
    	validate_each_argument(each_value_3);
    	let each_blocks_3 = [];

    	for (let i = 0; i < each_value_3.length; i += 1) {
    		each_blocks_3[i] = create_each_block_3(get_each_context_3(ctx, each_value_3, i));
    	}

    	let each_value_2 = /*icon*/ ctx[1]?.polygon ?? [];
    	validate_each_argument(each_value_2);
    	let each_blocks_2 = [];

    	for (let i = 0; i < each_value_2.length; i += 1) {
    		each_blocks_2[i] = create_each_block_2(get_each_context_2(ctx, each_value_2, i));
    	}

    	let each_value_1 = /*icon*/ ctx[1]?.polyline ?? [];
    	validate_each_argument(each_value_1);
    	let each_blocks_1 = [];

    	for (let i = 0; i < each_value_1.length; i += 1) {
    		each_blocks_1[i] = create_each_block_1(get_each_context_1(ctx, each_value_1, i));
    	}

    	let each_value = /*icon*/ ctx[1]?.line ?? [];
    	validate_each_argument(each_value);
    	let each_blocks = [];

    	for (let i = 0; i < each_value.length; i += 1) {
    		each_blocks[i] = create_each_block$1(get_each_context$1(ctx, each_value, i));
    	}

    	let svg_levels = [
    		/*icon*/ ctx[1]?.a,
    		{ xmlns: "http://www.w3.org/2000/svg" },
    		{ width: /*size*/ ctx[0] },
    		{ height: /*size*/ ctx[0] },
    		/*$$restProps*/ ctx[2]
    	];

    	let svg_data = {};

    	for (let i = 0; i < svg_levels.length; i += 1) {
    		svg_data = assign(svg_data, svg_levels[i]);
    	}

    	const block = {
    		c: function create() {
    			svg = svg_element("svg");

    			for (let i = 0; i < each_blocks_5.length; i += 1) {
    				each_blocks_5[i].c();
    			}

    			each0_anchor = empty();

    			for (let i = 0; i < each_blocks_4.length; i += 1) {
    				each_blocks_4[i].c();
    			}

    			each1_anchor = empty();

    			for (let i = 0; i < each_blocks_3.length; i += 1) {
    				each_blocks_3[i].c();
    			}

    			each2_anchor = empty();

    			for (let i = 0; i < each_blocks_2.length; i += 1) {
    				each_blocks_2[i].c();
    			}

    			each3_anchor = empty();

    			for (let i = 0; i < each_blocks_1.length; i += 1) {
    				each_blocks_1[i].c();
    			}

    			each4_anchor = empty();

    			for (let i = 0; i < each_blocks.length; i += 1) {
    				each_blocks[i].c();
    			}

    			set_svg_attributes(svg, svg_data);
    			add_location(svg, file$3, 16, 0, 376);
    		},
    		l: function claim(nodes) {
    			throw new Error("options.hydrate only works if the component was compiled with the `hydratable: true` option");
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, svg, anchor);

    			for (let i = 0; i < each_blocks_5.length; i += 1) {
    				each_blocks_5[i].m(svg, null);
    			}

    			append_dev(svg, each0_anchor);

    			for (let i = 0; i < each_blocks_4.length; i += 1) {
    				each_blocks_4[i].m(svg, null);
    			}

    			append_dev(svg, each1_anchor);

    			for (let i = 0; i < each_blocks_3.length; i += 1) {
    				each_blocks_3[i].m(svg, null);
    			}

    			append_dev(svg, each2_anchor);

    			for (let i = 0; i < each_blocks_2.length; i += 1) {
    				each_blocks_2[i].m(svg, null);
    			}

    			append_dev(svg, each3_anchor);

    			for (let i = 0; i < each_blocks_1.length; i += 1) {
    				each_blocks_1[i].m(svg, null);
    			}

    			append_dev(svg, each4_anchor);

    			for (let i = 0; i < each_blocks.length; i += 1) {
    				each_blocks[i].m(svg, null);
    			}
    		},
    		p: function update(ctx, [dirty]) {
    			if (dirty & /*icon*/ 2) {
    				each_value_5 = /*icon*/ ctx[1]?.path ?? [];
    				validate_each_argument(each_value_5);
    				let i;

    				for (i = 0; i < each_value_5.length; i += 1) {
    					const child_ctx = get_each_context_5(ctx, each_value_5, i);

    					if (each_blocks_5[i]) {
    						each_blocks_5[i].p(child_ctx, dirty);
    					} else {
    						each_blocks_5[i] = create_each_block_5(child_ctx);
    						each_blocks_5[i].c();
    						each_blocks_5[i].m(svg, each0_anchor);
    					}
    				}

    				for (; i < each_blocks_5.length; i += 1) {
    					each_blocks_5[i].d(1);
    				}

    				each_blocks_5.length = each_value_5.length;
    			}

    			if (dirty & /*icon*/ 2) {
    				each_value_4 = /*icon*/ ctx[1]?.rect ?? [];
    				validate_each_argument(each_value_4);
    				let i;

    				for (i = 0; i < each_value_4.length; i += 1) {
    					const child_ctx = get_each_context_4(ctx, each_value_4, i);

    					if (each_blocks_4[i]) {
    						each_blocks_4[i].p(child_ctx, dirty);
    					} else {
    						each_blocks_4[i] = create_each_block_4(child_ctx);
    						each_blocks_4[i].c();
    						each_blocks_4[i].m(svg, each1_anchor);
    					}
    				}

    				for (; i < each_blocks_4.length; i += 1) {
    					each_blocks_4[i].d(1);
    				}

    				each_blocks_4.length = each_value_4.length;
    			}

    			if (dirty & /*icon*/ 2) {
    				each_value_3 = /*icon*/ ctx[1]?.circle ?? [];
    				validate_each_argument(each_value_3);
    				let i;

    				for (i = 0; i < each_value_3.length; i += 1) {
    					const child_ctx = get_each_context_3(ctx, each_value_3, i);

    					if (each_blocks_3[i]) {
    						each_blocks_3[i].p(child_ctx, dirty);
    					} else {
    						each_blocks_3[i] = create_each_block_3(child_ctx);
    						each_blocks_3[i].c();
    						each_blocks_3[i].m(svg, each2_anchor);
    					}
    				}

    				for (; i < each_blocks_3.length; i += 1) {
    					each_blocks_3[i].d(1);
    				}

    				each_blocks_3.length = each_value_3.length;
    			}

    			if (dirty & /*icon*/ 2) {
    				each_value_2 = /*icon*/ ctx[1]?.polygon ?? [];
    				validate_each_argument(each_value_2);
    				let i;

    				for (i = 0; i < each_value_2.length; i += 1) {
    					const child_ctx = get_each_context_2(ctx, each_value_2, i);

    					if (each_blocks_2[i]) {
    						each_blocks_2[i].p(child_ctx, dirty);
    					} else {
    						each_blocks_2[i] = create_each_block_2(child_ctx);
    						each_blocks_2[i].c();
    						each_blocks_2[i].m(svg, each3_anchor);
    					}
    				}

    				for (; i < each_blocks_2.length; i += 1) {
    					each_blocks_2[i].d(1);
    				}

    				each_blocks_2.length = each_value_2.length;
    			}

    			if (dirty & /*icon*/ 2) {
    				each_value_1 = /*icon*/ ctx[1]?.polyline ?? [];
    				validate_each_argument(each_value_1);
    				let i;

    				for (i = 0; i < each_value_1.length; i += 1) {
    					const child_ctx = get_each_context_1(ctx, each_value_1, i);

    					if (each_blocks_1[i]) {
    						each_blocks_1[i].p(child_ctx, dirty);
    					} else {
    						each_blocks_1[i] = create_each_block_1(child_ctx);
    						each_blocks_1[i].c();
    						each_blocks_1[i].m(svg, each4_anchor);
    					}
    				}

    				for (; i < each_blocks_1.length; i += 1) {
    					each_blocks_1[i].d(1);
    				}

    				each_blocks_1.length = each_value_1.length;
    			}

    			if (dirty & /*icon*/ 2) {
    				each_value = /*icon*/ ctx[1]?.line ?? [];
    				validate_each_argument(each_value);
    				let i;

    				for (i = 0; i < each_value.length; i += 1) {
    					const child_ctx = get_each_context$1(ctx, each_value, i);

    					if (each_blocks[i]) {
    						each_blocks[i].p(child_ctx, dirty);
    					} else {
    						each_blocks[i] = create_each_block$1(child_ctx);
    						each_blocks[i].c();
    						each_blocks[i].m(svg, null);
    					}
    				}

    				for (; i < each_blocks.length; i += 1) {
    					each_blocks[i].d(1);
    				}

    				each_blocks.length = each_value.length;
    			}

    			set_svg_attributes(svg, svg_data = get_spread_update(svg_levels, [
    				dirty & /*icon*/ 2 && /*icon*/ ctx[1]?.a,
    				{ xmlns: "http://www.w3.org/2000/svg" },
    				dirty & /*size*/ 1 && { width: /*size*/ ctx[0] },
    				dirty & /*size*/ 1 && { height: /*size*/ ctx[0] },
    				dirty & /*$$restProps*/ 4 && /*$$restProps*/ ctx[2]
    			]));
    		},
    		i: noop,
    		o: noop,
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(svg);
    			destroy_each(each_blocks_5, detaching);
    			destroy_each(each_blocks_4, detaching);
    			destroy_each(each_blocks_3, detaching);
    			destroy_each(each_blocks_2, detaching);
    			destroy_each(each_blocks_1, detaching);
    			destroy_each(each_blocks, detaching);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_fragment$3.name,
    		type: "component",
    		source: "",
    		ctx
    	});

    	return block;
    }

    function instance$3($$self, $$props, $$invalidate) {
    	let icon;
    	const omit_props_names = ["src","size","theme"];
    	let $$restProps = compute_rest_props($$props, omit_props_names);
    	let { $$slots: slots = {}, $$scope } = $$props;
    	validate_slots('Icon', slots, []);
    	let { src } = $$props;
    	let { size = '100%' } = $$props;
    	let { theme = 'default' } = $$props;

    	if (size !== '100%') {
    		if (size.slice(-1) != 'x' && size.slice(-1) != 'm' && size.slice(-1) != '%') {
    			try {
    				size = parseInt(size) + 'px';
    			} catch(error) {
    				size = '100%';
    			}
    		}
    	}

    	$$self.$$.on_mount.push(function () {
    		if (src === undefined && !('src' in $$props || $$self.$$.bound[$$self.$$.props['src']])) {
    			console.warn("<Icon> was created without expected prop 'src'");
    		}
    	});

    	$$self.$$set = $$new_props => {
    		$$props = assign(assign({}, $$props), exclude_internal_props($$new_props));
    		$$invalidate(2, $$restProps = compute_rest_props($$props, omit_props_names));
    		if ('src' in $$new_props) $$invalidate(3, src = $$new_props.src);
    		if ('size' in $$new_props) $$invalidate(0, size = $$new_props.size);
    		if ('theme' in $$new_props) $$invalidate(4, theme = $$new_props.theme);
    	};

    	$$self.$capture_state = () => ({ src, size, theme, icon });

    	$$self.$inject_state = $$new_props => {
    		if ('src' in $$props) $$invalidate(3, src = $$new_props.src);
    		if ('size' in $$props) $$invalidate(0, size = $$new_props.size);
    		if ('theme' in $$props) $$invalidate(4, theme = $$new_props.theme);
    		if ('icon' in $$props) $$invalidate(1, icon = $$new_props.icon);
    	};

    	if ($$props && "$$inject" in $$props) {
    		$$self.$inject_state($$props.$$inject);
    	}

    	$$self.$$.update = () => {
    		if ($$self.$$.dirty & /*src, theme*/ 24) {
    			$$invalidate(1, icon = src?.[theme] ?? src?.['default']);
    		}
    	};

    	return [size, icon, $$restProps, src, theme];
    }

    class Icon extends SvelteComponentDev {
    	constructor(options) {
    		super(options);
    		init(this, options, instance$3, create_fragment$3, safe_not_equal, { src: 3, size: 0, theme: 4 });

    		dispatch_dev("SvelteRegisterComponent", {
    			component: this,
    			tagName: "Icon",
    			options,
    			id: create_fragment$3.name
    		});
    	}

    	get src() {
    		throw new Error("<Icon>: Props cannot be read directly from the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	set src(value) {
    		throw new Error("<Icon>: Props cannot be set directly on the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	get size() {
    		throw new Error("<Icon>: Props cannot be read directly from the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	set size(value) {
    		throw new Error("<Icon>: Props cannot be set directly on the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	get theme() {
    		throw new Error("<Icon>: Props cannot be read directly from the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}

    	set theme(value) {
    		throw new Error("<Icon>: Props cannot be set directly on the component instance unless compiling with 'accessors: true' or '<svelte:options accessors/>'");
    	}
    }

    const Dashboard = { "default": { "a": { "viewBox": "0 0 24 24", "fill": "currentColor" }, "path": [{ "fill": "none", "d": "M0 0h24v24H0z" }, { "d": "M13 21V11h8v10h-8zM3 13V3h8v10H3zm6-2V5H5v6h4zM3 21v-6h8v6H3zm2-2h4v-2H5v2zm10 0h4v-6h-4v6zM13 3h8v6h-8V3zm2 2v2h4V5h-4z" }] }, "solid": { "a": { "viewBox": "0 0 24 24", "fill": "currentColor" }, "path": [{ "fill": "none", "d": "M0 0h24v24H0z" }, { "d": "M3 13h8V3H3v10zm0 8h8v-6H3v6zm10 0h8V11h-8v10zm0-18v6h8V3h-8z" }] } };
    const Settings = { "default": { "a": { "viewBox": "0 0 24 24", "fill": "currentColor" }, "path": [{ "fill": "none", "d": "M0 0h24v24H0z" }, { "d": "M12 1l9.5 5.5v11L12 23l-9.5-5.5v-11L12 1zm0 2.311L4.5 7.653v8.694l7.5 4.342 7.5-4.342V7.653L12 3.311zM12 16a4 4 0 1 1 0-8 4 4 0 0 1 0 8zm0-2a2 2 0 1 0 0-4 2 2 0 0 0 0 4z" }] }, "solid": { "a": { "viewBox": "0 0 24 24", "fill": "currentColor" }, "path": [{ "fill": "none", "d": "M0 0h24v24H0z" }, { "d": "M12 1l9.5 5.5v11L12 23l-9.5-5.5v-11L12 1zm0 14a3 3 0 1 0 0-6 3 3 0 0 0 0 6z" }] } };

    /* src\Sidebar.svelte generated by Svelte v3.55.1 */
    const file$2 = "src\\Sidebar.svelte";

    function create_fragment$2(ctx) {
    	let ul;
    	let li0;
    	let span0;
    	let t1;
    	let li1;
    	let a0;
    	let icon0;
    	let t2;
    	let span1;
    	let t4;
    	let li2;
    	let a1;
    	let icon1;
    	let t5;
    	let span2;
    	let t7;
    	let li3;
    	let span3;
    	let t9;
    	let div;
    	let button0;
    	let t11;
    	let button1;
    	let t13;
    	let button2;
    	let current;

    	icon0 = new Icon({
    			props: { src: Dashboard, class: "w-5 h-5 mr-2" },
    			$$inline: true
    		});

    	icon1 = new Icon({
    			props: { src: Settings, class: "w-5 h-5 mr-2" },
    			$$inline: true
    		});

    	const block = {
    		c: function create() {
    			ul = element("ul");
    			li0 = element("li");
    			span0 = element("span");
    			span0.textContent = "Menu";
    			t1 = space();
    			li1 = element("li");
    			a0 = element("a");
    			create_component(icon0.$$.fragment);
    			t2 = space();
    			span1 = element("span");
    			span1.textContent = "Dashboard";
    			t4 = space();
    			li2 = element("li");
    			a1 = element("a");
    			create_component(icon1.$$.fragment);
    			t5 = space();
    			span2 = element("span");
    			span2.textContent = "Settings";
    			t7 = space();
    			li3 = element("li");
    			span3 = element("span");
    			span3.textContent = "Actions";
    			t9 = space();
    			div = element("div");
    			button0 = element("button");
    			button0.textContent = "Start";
    			t11 = space();
    			button1 = element("button");
    			button1.textContent = "Pause";
    			t13 = space();
    			button2 = element("button");
    			button2.textContent = "Stop";
    			add_location(span0, file$2, 6, 8, 237);
    			attr_dev(li0, "class", "menu-title");
    			add_location(li0, file$2, 5, 4, 204);
    			add_location(span1, file$2, 13, 12, 445);
    			attr_dev(a0, "href", "#");
    			attr_dev(a0, "class", "menu-item");
    			add_location(a0, file$2, 11, 8, 342);
    			add_location(li1, file$2, 9, 4, 273);
    			add_location(span2, file$2, 20, 12, 669);
    			attr_dev(a1, "href", "#");
    			attr_dev(a1, "class", "menu-item");
    			add_location(a1, file$2, 18, 8, 567);
    			add_location(li2, file$2, 16, 4, 498);
    			add_location(span3, file$2, 26, 8, 783);
    			attr_dev(li3, "class", "menu-title mt-6");
    			add_location(li3, file$2, 25, 4, 745);
    			attr_dev(button0, "class", "btn bg-green-500 hover:bg-green-600 text-white rounded-btn");
    			add_location(button0, file$2, 30, 8, 875);
    			attr_dev(button1, "class", "btn bg-orange-500 hover:bg-orange-600 text-white rounded-btn");
    			add_location(button1, file$2, 35, 8, 1021);
    			attr_dev(button2, "class", "btn bg-red-600 hover:bg-red-700 text-white rounded-btn");
    			add_location(button2, file$2, 40, 8, 1169);
    			attr_dev(div, "class", "btn-group flex justify-center");
    			add_location(div, file$2, 29, 4, 822);
    			attr_dev(ul, "class", "menu p-4 w-80 bg-base-300 text-base-content");
    			add_location(ul, file$2, 4, 0, 142);
    		},
    		l: function claim(nodes) {
    			throw new Error("options.hydrate only works if the component was compiled with the `hydratable: true` option");
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, ul, anchor);
    			append_dev(ul, li0);
    			append_dev(li0, span0);
    			append_dev(ul, t1);
    			append_dev(ul, li1);
    			append_dev(li1, a0);
    			mount_component(icon0, a0, null);
    			append_dev(a0, t2);
    			append_dev(a0, span1);
    			append_dev(ul, t4);
    			append_dev(ul, li2);
    			append_dev(li2, a1);
    			mount_component(icon1, a1, null);
    			append_dev(a1, t5);
    			append_dev(a1, span2);
    			append_dev(ul, t7);
    			append_dev(ul, li3);
    			append_dev(li3, span3);
    			append_dev(ul, t9);
    			append_dev(ul, div);
    			append_dev(div, button0);
    			append_dev(div, t11);
    			append_dev(div, button1);
    			append_dev(div, t13);
    			append_dev(div, button2);
    			current = true;
    		},
    		p: noop,
    		i: function intro(local) {
    			if (current) return;
    			transition_in(icon0.$$.fragment, local);
    			transition_in(icon1.$$.fragment, local);
    			current = true;
    		},
    		o: function outro(local) {
    			transition_out(icon0.$$.fragment, local);
    			transition_out(icon1.$$.fragment, local);
    			current = false;
    		},
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(ul);
    			destroy_component(icon0);
    			destroy_component(icon1);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_fragment$2.name,
    		type: "component",
    		source: "",
    		ctx
    	});

    	return block;
    }

    function instance$2($$self, $$props, $$invalidate) {
    	let { $$slots: slots = {}, $$scope } = $$props;
    	validate_slots('Sidebar', slots, []);
    	const writable_props = [];

    	Object.keys($$props).forEach(key => {
    		if (!~writable_props.indexOf(key) && key.slice(0, 2) !== '$$' && key !== 'slot') console.warn(`<Sidebar> was created with unknown prop '${key}'`);
    	});

    	$$self.$capture_state = () => ({ Icon, Settings, Dashboard });
    	return [];
    }

    class Sidebar extends SvelteComponentDev {
    	constructor(options) {
    		super(options);
    		init(this, options, instance$2, create_fragment$2, safe_not_equal, {});

    		dispatch_dev("SvelteRegisterComponent", {
    			component: this,
    			tagName: "Sidebar",
    			options,
    			id: create_fragment$2.name
    		});
    	}
    }

    const recordings = [
        {
            id: "1",
            title: "Video Title",
            duration: 3600,
            date: "2021-12-28",
            thumbnail: "https://picsum.photos/seed/picsum/1280/720",
        },
        {
            id: "2",
            title: "Video Title",
            duration: 3600,
            date: "2021-12-28",
            thumbnail: "https://picsum.photos/seed/picsum/1280/720",
        },
        {
            id: "3",
            title: "Video Title",
            duration: 3600,
            date: "2021-12-28",
            thumbnail: "https://picsum.photos/seed/picsum/1280/720",
        },
        {
            id: "4",
            title: "Video Title",
            duration: 3600,
            date: "2021-12-28",
            thumbnail: "https://picsum.photos/seed/picsum/1280/720",
        },
        {
            id: "5",
            title: "Video Title",
            duration: 3600,
            date: "2021-12-28",
            thumbnail: "https://picsum.photos/seed/picsum/1280/720",
        },
        {
            id: "6",
            title: "Video Title",
            duration: 3600,
            date: "2021-12-28",
            thumbnail: "https://picsum.photos/seed/picsum/1280/720",
        },
        {
            id: "7",
            title: "Video Title",
            duration: 3600,
            date: "2021-12-28",
            thumbnail: "https://picsum.photos/seed/picsum/1280/720",
        },
        {
            id: "8",
            title: "Video Title",
            duration: 3600,
            date: "2021-12-28",
            thumbnail: "https://picsum.photos/seed/picsum/1280/720",
        },
        {
            id: "9",
            title: "Video Title",
            duration: 3600,
            date: "2021",
            thumbnail: "https://picsum.photos/seed/picsum/1280/720",
        }
    ];

    /* src\Content.svelte generated by Svelte v3.55.1 */
    const file$1 = "src\\Content.svelte";

    function get_each_context(ctx, list, i) {
    	const child_ctx = ctx.slice();
    	child_ctx[0] = list[i];
    	return child_ctx;
    }

    // (16:8) {#each recordings as recording}
    function create_each_block(ctx) {
    	let div4;
    	let figure;
    	let img;
    	let img_src_value;
    	let t0;
    	let div3;
    	let h2;
    	let t1_value = /*recording*/ ctx[0].title + "";
    	let t1;
    	let t2;
    	let div2;
    	let div0;
    	let t3_value = /*recording*/ ctx[0].duration + "";
    	let t3;
    	let t4;
    	let div1;
    	let t5_value = /*recording*/ ctx[0].date + "";
    	let t5;
    	let t6;

    	const block = {
    		c: function create() {
    			div4 = element("div");
    			figure = element("figure");
    			img = element("img");
    			t0 = space();
    			div3 = element("div");
    			h2 = element("h2");
    			t1 = text(t1_value);
    			t2 = space();
    			div2 = element("div");
    			div0 = element("div");
    			t3 = text(t3_value);
    			t4 = space();
    			div1 = element("div");
    			t5 = text(t5_value);
    			t6 = space();
    			if (!src_url_equal(img.src, img_src_value = /*recording*/ ctx[0].thumbnail)) attr_dev(img, "src", img_src_value);
    			attr_dev(img, "alt", "thumbnail");
    			add_location(img, file$1, 20, 20, 843);
    			add_location(figure, file$1, 19, 16, 813);
    			attr_dev(h2, "class", "card-title first-letter:uppercase");
    			add_location(h2, file$1, 23, 20, 982);
    			attr_dev(div0, "class", "badge badge-outline");
    			add_location(div0, file$1, 28, 24, 1186);
    			attr_dev(div1, "class", "badge badge-outline");
    			add_location(div1, file$1, 31, 24, 1327);
    			attr_dev(div2, "class", "card-actions justify-end");
    			add_location(div2, file$1, 27, 20, 1122);
    			attr_dev(div3, "class", "card-body");
    			add_location(div3, file$1, 22, 16, 937);
    			attr_dev(div4, "class", "card card-compact bg-base-300 shadow-xl hover:cursor-pointer hover:scale-105 transition-transform");
    			add_location(div4, file$1, 16, 12, 653);
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, div4, anchor);
    			append_dev(div4, figure);
    			append_dev(figure, img);
    			append_dev(div4, t0);
    			append_dev(div4, div3);
    			append_dev(div3, h2);
    			append_dev(h2, t1);
    			append_dev(div3, t2);
    			append_dev(div3, div2);
    			append_dev(div2, div0);
    			append_dev(div0, t3);
    			append_dev(div2, t4);
    			append_dev(div2, div1);
    			append_dev(div1, t5);
    			append_dev(div4, t6);
    		},
    		p: noop,
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(div4);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_each_block.name,
    		type: "each",
    		source: "(16:8) {#each recordings as recording}",
    		ctx
    	});

    	return block;
    }

    function create_fragment$1(ctx) {
    	let div3;
    	let div1;
    	let h1;
    	let t1;
    	let div0;
    	let button0;
    	let t3;
    	let button1;
    	let t5;
    	let div2;
    	let each_value = recordings;
    	validate_each_argument(each_value);
    	let each_blocks = [];

    	for (let i = 0; i < each_value.length; i += 1) {
    		each_blocks[i] = create_each_block(get_each_context(ctx, each_value, i));
    	}

    	const block = {
    		c: function create() {
    			div3 = element("div");
    			div1 = element("div");
    			h1 = element("h1");
    			h1.textContent = "Dashboard";
    			t1 = space();
    			div0 = element("div");
    			button0 = element("button");
    			button0.textContent = "New";
    			t3 = space();
    			button1 = element("button");
    			button1.textContent = "Filter";
    			t5 = space();
    			div2 = element("div");

    			for (let i = 0; i < each_blocks.length; i += 1) {
    				each_blocks[i].c();
    			}

    			attr_dev(h1, "class", "text-3xl font-bold");
    			add_location(h1, file$1, 6, 8, 178);
    			attr_dev(button0, "class", "btn btn-ghost btn-sm rounded-btn");
    			add_location(button0, file$1, 8, 12, 288);
    			attr_dev(button1, "class", "btn btn-ghost btn-sm rounded-btn");
    			add_location(button1, file$1, 9, 12, 363);
    			attr_dev(div0, "class", "flex items-center space-x-4");
    			add_location(div0, file$1, 7, 8, 233);
    			attr_dev(div1, "class", "flex justify-between items-center");
    			add_location(div1, file$1, 5, 4, 121);
    			attr_dev(div2, "class", "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mt-6");
    			add_location(div2, file$1, 14, 4, 527);
    			attr_dev(div3, "class", "p-6 pb-16");
    			add_location(div3, file$1, 3, 0, 72);
    		},
    		l: function claim(nodes) {
    			throw new Error("options.hydrate only works if the component was compiled with the `hydratable: true` option");
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, div3, anchor);
    			append_dev(div3, div1);
    			append_dev(div1, h1);
    			append_dev(div1, t1);
    			append_dev(div1, div0);
    			append_dev(div0, button0);
    			append_dev(div0, t3);
    			append_dev(div0, button1);
    			append_dev(div3, t5);
    			append_dev(div3, div2);

    			for (let i = 0; i < each_blocks.length; i += 1) {
    				each_blocks[i].m(div2, null);
    			}
    		},
    		p: function update(ctx, [dirty]) {
    			if (dirty & /*recordings*/ 0) {
    				each_value = recordings;
    				validate_each_argument(each_value);
    				let i;

    				for (i = 0; i < each_value.length; i += 1) {
    					const child_ctx = get_each_context(ctx, each_value, i);

    					if (each_blocks[i]) {
    						each_blocks[i].p(child_ctx, dirty);
    					} else {
    						each_blocks[i] = create_each_block(child_ctx);
    						each_blocks[i].c();
    						each_blocks[i].m(div2, null);
    					}
    				}

    				for (; i < each_blocks.length; i += 1) {
    					each_blocks[i].d(1);
    				}

    				each_blocks.length = each_value.length;
    			}
    		},
    		i: noop,
    		o: noop,
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(div3);
    			destroy_each(each_blocks, detaching);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_fragment$1.name,
    		type: "component",
    		source: "",
    		ctx
    	});

    	return block;
    }

    function instance$1($$self, $$props, $$invalidate) {
    	let { $$slots: slots = {}, $$scope } = $$props;
    	validate_slots('Content', slots, []);
    	const writable_props = [];

    	Object.keys($$props).forEach(key => {
    		if (!~writable_props.indexOf(key) && key.slice(0, 2) !== '$$' && key !== 'slot') console.warn(`<Content> was created with unknown prop '${key}'`);
    	});

    	$$self.$capture_state = () => ({ recordings });
    	return [];
    }

    class Content extends SvelteComponentDev {
    	constructor(options) {
    		super(options);
    		init(this, options, instance$1, create_fragment$1, safe_not_equal, {});

    		dispatch_dev("SvelteRegisterComponent", {
    			component: this,
    			tagName: "Content",
    			options,
    			id: create_fragment$1.name
    		});
    	}
    }

    /* src\App.svelte generated by Svelte v3.55.1 */
    const file = "src\\App.svelte";

    function create_fragment(ctx) {
    	let div2;
    	let input;
    	let t0;
    	let div0;
    	let content;
    	let t1;
    	let div1;
    	let label;
    	let t2;
    	let sidebar;
    	let current;
    	content = new Content({ $$inline: true });
    	sidebar = new Sidebar({ $$inline: true });

    	const block = {
    		c: function create() {
    			div2 = element("div");
    			input = element("input");
    			t0 = space();
    			div0 = element("div");
    			create_component(content.$$.fragment);
    			t1 = space();
    			div1 = element("div");
    			label = element("label");
    			t2 = space();
    			create_component(sidebar.$$.fragment);
    			attr_dev(input, "id", "sideBtn");
    			attr_dev(input, "type", "checkbox");
    			attr_dev(input, "class", "drawer-toggle");
    			add_location(input, file, 5, 4, 153);
    			attr_dev(div0, "class", "drawer-content");
    			add_location(div0, file, 6, 4, 219);
    			attr_dev(label, "for", "sideBtn");
    			attr_dev(label, "class", "drawer-overlay");
    			add_location(label, file, 10, 8, 337);
    			attr_dev(div1, "class", "drawer-side grid-flow-dense");
    			add_location(div1, file, 9, 4, 286);
    			attr_dev(div2, "class", "drawer drawer-mobile");
    			add_location(div2, file, 4, 0, 113);
    		},
    		l: function claim(nodes) {
    			throw new Error("options.hydrate only works if the component was compiled with the `hydratable: true` option");
    		},
    		m: function mount(target, anchor) {
    			insert_dev(target, div2, anchor);
    			append_dev(div2, input);
    			append_dev(div2, t0);
    			append_dev(div2, div0);
    			mount_component(content, div0, null);
    			append_dev(div2, t1);
    			append_dev(div2, div1);
    			append_dev(div1, label);
    			append_dev(div1, t2);
    			mount_component(sidebar, div1, null);
    			current = true;
    		},
    		p: noop,
    		i: function intro(local) {
    			if (current) return;
    			transition_in(content.$$.fragment, local);
    			transition_in(sidebar.$$.fragment, local);
    			current = true;
    		},
    		o: function outro(local) {
    			transition_out(content.$$.fragment, local);
    			transition_out(sidebar.$$.fragment, local);
    			current = false;
    		},
    		d: function destroy(detaching) {
    			if (detaching) detach_dev(div2);
    			destroy_component(content);
    			destroy_component(sidebar);
    		}
    	};

    	dispatch_dev("SvelteRegisterBlock", {
    		block,
    		id: create_fragment.name,
    		type: "component",
    		source: "",
    		ctx
    	});

    	return block;
    }

    function instance($$self, $$props, $$invalidate) {
    	let { $$slots: slots = {}, $$scope } = $$props;
    	validate_slots('App', slots, []);
    	const writable_props = [];

    	Object.keys($$props).forEach(key => {
    		if (!~writable_props.indexOf(key) && key.slice(0, 2) !== '$$' && key !== 'slot') console.warn(`<App> was created with unknown prop '${key}'`);
    	});

    	$$self.$capture_state = () => ({ Sidebar, Content });
    	return [];
    }

    class App extends SvelteComponentDev {
    	constructor(options) {
    		super(options);
    		init(this, options, instance, create_fragment, safe_not_equal, {});

    		dispatch_dev("SvelteRegisterComponent", {
    			component: this,
    			tagName: "App",
    			options,
    			id: create_fragment.name
    		});
    	}
    }

    const app = new App({
        target: document.querySelector('body')
    });

    return app;

})();
//# sourceMappingURL=bundle.js.map
