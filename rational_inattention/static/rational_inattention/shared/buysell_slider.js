import { html, PolymerElement } from '/static/otree-redwood/node_modules/@polymer/polymer/polymer-element.js';
import '../polymer-elements/paper-range-slider.js';
import './price_marker.js';
// import '../polymer-elements/paper-single-range-slider.js';

class BuysellSlider extends PolymerElement {
    static get properties() {
        return {
            buyPrice: {
                type: Number,
                value: 100,
                notify: true,
                reflectToAttribute: true,
            },
            sellPrice: {
                type: Number,
                value: 0,
                notify: true,
                reflectToAttribute: true,
            },
            markers: {
                type: Array,
                value: [0, , , , , 100],
            },
            priceToShow: Number,
            animatePrice: {
                type: Boolean,
            },
        }
    }

    static get template() {
        // paper-slider seems to be incompatible with ::input
        return html`
            <style>
                :host {
                    position: relative;
                }
                #price {
                    --mark-color: var(--price-color);
                    opacity: 0;
                }
                #anim {
                    background-color: var(--price-color);
                }
                .ball {
                    position: absolute;
                    width: 20px;
                    height: 20px;
                    display: block;
                    left: 50%;
                    border-radius: 50%;
                    bottom: -35px;
                    z-index: 1;
                }
                .hid {
                    opacity: 0;
                }
                .markers {
                    position: relative;
                    display: flex;
                    height: 16px;
                    margin: 0 24px 0 5px;
                }
                .high {
                    --mark-color: #CCCC00;
                }
                .low {
                    --mark-color: #7A70CC;
                }
                .sliderticks {
                    display: flex;
                    justify-content: space-between;
                    position: relative;
                    height: 8px;
                }
                .sliderticks p {
                    position: relative;
                    display: flex;
                    justify-content: center;
                    text-align: center;
                    margin: 0;
                }
                .slider1 {
                    --paper-range-slider-higher-knob-color: #007bff;
                    --paper-range-slider-higher-pin-color: #007bff;
                    --paper-range-slider-lower-knob-color: #2F3238;
                    --paper-range-slider-lower-pin-color: #2F3238;
                    --paper-range-slider-active-color: #A9A9A9;
                    width: 100%;
                }
            </style>
            <div class="markers">
                <price-marker
                class="high"
                value="[[ highValue ]]"
                style$="left: [[ _getMark(highValue) ]]%;"
            ></price-marker>
            <price-marker
                class="low"
                value="[[ lowValue ]]"
                style$="left: [[ _getMark(lowValue) ]]%;"
            ></price-marker>
            <price-marker
                id="price"
                value="[[ priceToShow ]]"
                style$="left: {{ _getMark(priceToShow) }}%;"
                hidden$="[[ _hidePrice(hideBeforeSubmit, animatePrice) ]]"
            ></price-marker>
            </div>
            <div class="markers">
                <span id="anim" class$="[[ _showActualPrice(animatePrice, priceToShow, hideBeforeSubmit) ]]" hidden$="[[ _hidePrice(hideBeforeSubmit, animatePrice) ]]"></span>
            </div>
            <div class="sliderticks">
                <template is="dom-repeat" items="[[ markers ]]">
                    <p>[[ item ]]</p>
                </template>
            </div>
            <div hidden$="[[ sellOption ]]">
                <paper-single-range-slider
                    class="slider1"
                    slider-width="100%"
                    pin
                    always-show-pin
                    min="0"
                    max="100"
                    step="0.1"
                    value="{{ buyPrice::change }}"
                    disabled="[[ disableSelect ]]"
                ></paper-single-range-slider>
            </div>
            <div hidden$="[[ buyOption ]]">
                <paper-single-range-slider
                    class="slider1"
                    slider-width="100%"
                    pin
                    always-show-pin
                    min="0"
                    max="100"
                    step="0.1"
                    value="{{ sellPrice::change }}"
                    disabled="[[ disableSelect ]]"
                ></paper-single-range-slider>
            </div>
            <div hidden$="[[ _hideSlider(buyOption, sellOption) ]]">
                <paper-range-slider
                    class="slider1"
                    slider-width="100%"
                    always-show-pin
                    min="0"
                    max="100"
                    step="0.1"
                    value-min="{{ buyPrice::change }}"
                    value-max="{{ sellPrice::change }}"
                    disabled="[[ disableSelect ]]"
                ></paper-range-slider>
            </div>
        `;
    }

    _hidePrice(hideBeforeSubmit, animatePrice) {
        if (animatePrice)
            return false;
        else
            return hideBeforeSubmit;
    }

    _showActualPrice(animatePrice, priceToShow, hideBeforeSubmit) {
        let pos = (this._getMark(priceToShow)).toString() + '%';
        if (animatePrice) {
            // back and forth
            let anim = this.$.anim.animate([
                { left: '50%' },
                { left: '100%' },
                { left: 0 },
            ], {
                duration: 4000,
                easing: 'ease-in-out', // 'linear', a bezier curve, etc.
                delay: 1000, // milliseconds
                direction: 'alternate', // 'normal', 'reverse', etc.
                fill: 'forwards'
            });

            // stops at more accurate position above marker
            anim.onfinish = () => {
                this.$.anim.animate([
                    { left: 0 },
                    { left: pos },
                ], {
                    duration: 2000,
                    easing: 'ease-in-out',
                    direction: 'alternate',
                    fill: 'forwards'
                });
                // show price marker right after
                this.$.price.animate([
                    { opacity: 0 },
                    { opacity: 1 },
                ], {
                    duration: 2000,
                    easing: 'ease-in',
                    delay: 1000,
                    fill: 'forwards'
                });
            }
            return 'ball';
        }
        else if (!hideBeforeSubmit) {
            this.$.anim.animate([
                { opacity: 0 },
                { opacity: 1 },
                { left: pos },
            ], {
                duration: 2000,
                easing: 'ease-in',
                fill: 'forwards'
            });
            // show price marker right after
            // this is what's causing the marker to appear beforehand
            this.$.price.animate([
                { left: pos },
                { opacity: 0 },
                { opacity: 1 },
                { opacity: 1 },
                { opacity: 1 },
                { opacity: 1 },
                { opacity: 1 },
                { opacity: 1 },
                { opacity: 1 },
            ], {
                duration: 4000,
                easing: 'ease-in-out',


            });
            return 'ball';
        }
        return 'ball hid';
    }

    _getMark(val) {
        return val;
    }

    _hideSlider(buyOption, sellOption) {
        // show double slider
        if (buyOption && sellOption)
            return false;
        else
            return true;
    }
}

window.customElements.define('buysell-slider', BuysellSlider);
