import { html, PolymerElement } from '/static/otree-redwood/node_modules/@polymer/polymer/polymer-element.js';
import '../shared/buysell_slider.js';
class BondPrice extends PolymerElement {

    static get properties() {
        return {
            e: {
                type: Number,
            },
            mLow: {
                type: Number,
                computed: '_getMLow(m, precision)',
                observer: '_getLowValue',
                notify: true,
                reflectToAttribute: true,
            },
            mHigh: {
                type: Number,
                computed: '_getMHigh(m, precision)',
                observer: '_getHighValue',
                notify: true,
                reflectToAttribute: true,
            },
            highValue: {
                type: Number,
                computed: '_getHighValue(defaultProb, mHigh)',
                notify: true,
                reflectToAttribute: true,
            },
            lowValue: {
                type: Number,
                computed: '_getLowValue(defaultProb, mLow)',
                notify: true,
                reflectToAttribute: true,
            },
            buyPrice: {
                type: Number,
                notify: true,
                value: 0,
                reflectToAttribute: true,
            },
            sellPrice: {
                type: Number,
                notify: true,
                value: 100,
                reflectToAttribute: true,
            },
            expectedValue: {
                type: Number,
                computed: '_expectedBondVal(m)',
                notify: true,
                reflectToAttribute: true,
            },
            scale: {
                type: Number,
                value: 100,
            }
        }
    }

    static get template() {
        return html`
        <style>
            .values {
                text-align: center;
            }
            .def {
                color: #DF5353;
            }
            .non-def {
                color: #55BF3B;
            }
            .buy-sell-text {
                text-align: left;
            }
            .val {
                font-weight: bold;
            }
            .low {
                color: #7A70CC;
            }
            .high {
                color: #CCCC00;
            }
            .buy {
                color: #2F3238;
            }
            #buy_warning {
                color: red;
            }
            #sell_warning {
                color: red;
            }
            .sell {
                color: #007bff;
            }
            .slider {
                --price-color: #F06292;
            }
            .exp-val {
                color: #F06292;
            }
            #substep {
                opacity: 0;
            }
            img {
                height: 2em;
            }
        </style>
        <div class="values">

        <h3>Your private information about m: [[ mLow ]] <span>&#8804;</span> m <span>&#8804;</span> [[ mHigh ]]</h3>

        <h4 hidden$="[[ sellOption ]]">Select the price for which you'd like to <span class="buy val">buy</span> the bond by sliding
        <img src="../../../../../static/rational_inattention/shared/buy_marker.png" alt="buy marker failed to load :(">
        <span class="buy val">(bid)</span>.</h4>

        <h4 hidden$="[[ buyOption ]]">Select the price for which you'd like to <span class="sell val">sell</span> the bond by sliding
        <img src="../../../../../static/rational_inattention/shared/sell_marker.png" alt="buy marker failed to load :(">
        <span class="sell val">(ask)</span>.</h4>

        <p class = "buy-sell-text" hidden$="[[ _hideOption(buyOption, sellOption) ]]">
            Select the price for which you'd like to <span class="buy val">buy</span> the bond by sliding
        <img src="../../../../../static/rational_inattention/shared/buy_marker.png" alt="buy marker failed to load :(">
        <span class="buy val">(bid)</span>, and the price for which you'd like to <span class="sell val">sell</span>
        the bond by sliding
        <img src="../../../../../static/rational_inattention/shared/sell_marker.png" alt="buy marker failed to load :(">
        <span class="sell val">(ask)</span>.</p>

           <!-- <p>Assuming you don't care about uncertainty, you would expect:</p> -->
            <p>Lowest expected bond value: <span class="non-def">[[ _getNondefault(defaultProb) ]]%</span> * 100 + <span class="def">[[ defaultProb ]]%</span>
            * [[ mLow ]] = <span class="low val">[[ lowValue ]]</span></p>
            <p>Highest expected bond value: <span class="non-def">[[ _getNondefault(defaultProb) ]]%</span> * 100 + <span class="def">[[ defaultProb ]]%</span>
            * [[ mHigh ]] = <span class="high val">[[ highValue ]]</span></p>

            <buysell-slider
                class="slider"
                m="[[ m ]]"
                low-value="[[ lowValue ]]"
                high-value="[[ highValue ]]"
                buy-option="{{ buyOption }}"
                sell-option="{{ sellOption }}"
                buy-price="{{ buyPrice }}"
                sell-price="{{ sellPrice }}"
                hide-before-submit="{{ hideBeforeSubmit }}"
                price-to-show="[[ expectedValue ]]"
                disable-select="[[ disableSelect ]]"
                animate-price="[[ animatePrice ]]"
            ></buysell-slider>
            <div id="buy_warning" hidden$ = "[[ _hide_buy_Warning(buyPrice) ]]">
                <p>Warning: your bid node currently rests at the default position.</p>
            </div>
            <div id="sell_warning" hidden$ ="[[ _hide_sell_Warning(sellPrice) ]]" >
                <p> Warning: your ask node currently rests at the default position. </p>
            </div>
            <div id="substep" hidden$="[[ _hideM(hideBeforeSubmit) ]]">
                <h2>Actual m: [[ m ]]</h2>
                <h3>Expected bond value:
                <span class="non-def">[[ _getNondefault(g) ]]%</span> * 100 + <span class="def">[[ g ]]%</span>
                    * [[ m ]] = <span class="exp-val">[[ expectedValue ]]</span>
                </h3>
            </div>
        </div>
        `;
    }

    _hideM(hideBeforeSubmit) {
        if(!hideBeforeSubmit) {
            this.$.substep.animate([
                { opacity: 0 },
                { opacity: 1 },
            ], {
                duration: 1000, // milliseconds
                easing: 'ease-in',
                fill: 'forwards',
            });
        }
        return hideBeforeSubmit;
    }
    _hide_buy_Warning(buyPrice) {
      if(this.buyOption) {
        if(buyPrice == 0)
          return false;
          else
            return true;
        }
        else
          return true;
      }

    _hide_sell_Warning(sellPrice) {
      if(this.sellOption) {
        if(sellPrice == 100)
          return false;
          else
            return true;
        }
        else
          return true;
      }

    _hideOption(buyOption, sellOption) {
        // buy = 0, sell = 1
        if (buyOption && sellOption)
            return false;
        else
            return true;
    }

    _getNondefault(def) {
        return 100 - def;
    }

    _expectedBondVal(m) {
        return parseFloat((this._getNondefault(this.g) + this.g * m / 100).toFixed(2));
    }

    _getRandomRange() {
        return Math.random();
    }

    _getMLowOverflow(m, precision) {
        let mLow = m - (precision * this.e);
        if (mLow < 0) {
            let overflow = 0 - mLow;
            return overflow;
        }
        return 0;
    }

    _getMHighOverflow(m, precision) {
        let mHigh = m + (precision * (1 - this.e));
        if (mHigh > this.scale) {
            let overflow = mHigh - this.scale;
            return overflow;
        }
        return 0;
    }

    _getMHigh(m, precision) {
        let mHigh = Math.min(this.scale, m + (precision * (1 - this.e)) + this._getMLowOverflow(m, precision));
        return parseFloat(mHigh.toFixed(2));
    }

    _getMLow(m, precision) {
        let mLow = Math.max(0, m - (precision * this.e) - this._getMHighOverflow(m, precision));
        return parseFloat(mLow.toFixed(2));
    }

    _getHighValue(defaultProb, mHigh) {
        return parseFloat((this._getNondefault(defaultProb) + defaultProb * mHigh / this.scale).toFixed(2));

    }

    _getLowValue(defaultProb, mLow) {
        return parseFloat((this._getNondefault(defaultProb) + defaultProb * mLow / this.scale).toFixed(2));
    }

    _getNondefault(def) {
        return parseInt(this.scale - def);
    }
}

window.customElements.define('bond-price', BondPrice);
