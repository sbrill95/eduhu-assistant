/******/ (() => { // webpackBootstrap
/******/ 	"use strict";

;// ./src/utils.js
/** @constant {number} DEBOUNCE_DELAY_MS Debounce delay to use */
const DEBOUNCE_DELAY_MS = 40;

/** @constant {number} DEFAULT_LINE_HEIGHT Default line height when it is "normal" */
const DEFAULT_LINE_HEIGHT = 1.2;

/** @constant {number} CLOSE_TO_INTEGER_EPSILON Epsilon for closeness to integer */
const CLOSE_TO_INTEGER_EPSILON = 0.01;

/**
 * Strips html tags and converts special characters.
 * Example: "<div>Me &amp; you</div>" is converted to "Me & you".
 *
 * @param {String} text The text to be parsed
 * @returns {String} The parsed text
 */
const parseString = text => {
  if (text === null || text === undefined) {
    return '';
  }
  const div = document.createElement('div');
  div.innerHTML = text;
  return div.textContent;
};

/**
 * Create an HTML element, and apply potential options/css
 *
 * @param {string} tag The HTML tag to create
 * @param {object} options Options like classList, textContent etc.
 * @param {object} style Styles/css to apply to the element
 * @returns
 */
const createElement = (tag, options, style = {}) => {
  const element = Object.assign(document.createElement(tag), options);
  Object.assign(element.style, style);
  return element;
};
/**
 * Compute the number of lines in an element.
 * @param {HTMLElement} element The element to compute lines for.
 * @returns {number} The number of lines in the element.
 */
const computeLineCount = element => {
  if (!element) {
    return 0;
  }
  const style = getComputedStyle(element);
  let lineHeight = parseFloat(style.lineHeight);
  if (isNaN(lineHeight)) {
    const fontSize = parseFloat(style.fontSize);
    lineHeight = fontSize * DEFAULT_LINE_HEIGHT;
  }
  const elementHeight = element.getBoundingClientRect().height;
  const numberOfLinesExact = elementHeight / lineHeight;

  // Element height might be slightly larger only, then assuming one more line is not correct.
  const floatingValue = Math.abs(Math.round(numberOfLinesExact) - numberOfLinesExact);
  const isCloseToInteger = floatingValue < CLOSE_TO_INTEGER_EPSILON;
  return isCloseToInteger ? Math.round(numberOfLinesExact) : Math.ceil(numberOfLinesExact);
};

/**
 * Compute the width ratio between two elements.
 * @param {HTMLElement} elementA The first element.
 * @param {HTMLElement} elementB The second element.
 * @returns {number} The width ratio (elementA / elementB).
 */
const computeWidthRatio = (elementA, elementB) => {
  if (!elementA || !elementB) {
    return 0;
  }
  const widthA = elementA.offsetWidth;
  const widthB = elementB.clientWidth;
  if (!widthA || !widthB) {
    return 0;
  }
  return widthA / widthB;
};

/**
 * Debounce a function call.
 * @param {function} callback Function to debounce.
 * @param {number} delayMs Debouncing delay.
 * @returns {function} Debounced function.
 */
const debounce = (callback, delayMs = DEBOUNCE_DELAY_MS) => {
  let timeoutId;
  return (...args) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => callback(...args), delayMs);
  };
};
;// ./src/components/h5p-button.js



/** @constant {number} MAX_LABEL_LINE_COUNT Maximum number of lines for label before hiding it */
const MAX_LABEL_LINE_COUNT = 1;

/**
 * @constant {number} MAX_LABEL_WIDTH_RATIO
 * Maximum width ratio between label and button before hiding label */
const MAX_LABEL_WIDTH_RATIO = 0.85;

/**
 * @typedef {'primary' | 'secondary' | 'nav'} ButtonStyleType
 */

/**
 * @typedef {
 *   'check' |
 *   'retry' |
 *   'done' |
 *   'show-results' |
 *   'book' |
 *   'flip' |
 *   'next' |
 *   'previous' |
 *   'show-solutions'
 * } ButtonIcon
 */

/**
 * @typedef ButtonParams
 * @type {object}
 * @property {string} [label] The button text
 * @property {string} [ariaLabel] The screenreader friendly text. Default is label
 * @property {string} [tooltip] The tooltip to show on hover/focus. Default is label if icon enabled
 *    Needed since icon only button on small screens
 * @property {ButtonStyleType} [styleType] Which (visual) type of button it is
 * @property {ButtonIcon} [icon] Which icon to show on the button
 * @property {string[]} [classes] Additional classes to add to the button
 * @property {Function} [onClick] The function to perform once the button is clicked
 * @property {string} [buttonType] Which html type the button should be. Default is button
 * @property {boolean} [disabled] Whether the button should be enabled/disabled. Default is enabled
 */

/**
 * Create a themed, responsive button
 * @param {ButtonParams} params A set of parameters to configure the Button component
 * @returns {HTMLElement} The button element
 */
function Button(params) {
  const baseClass = 'h5p-theme-button';
  let buttonStyleType = 'h5p-theme-primary-cta';
  if (params.styleType === 'secondary') {
    buttonStyleType = 'h5p-theme-secondary-cta';
  } else if (params.styleType === 'nav') {
    buttonStyleType = 'h5p-theme-nav-button';
  }
  buttonStyleType = `${baseClass} ${buttonStyleType}`;
  let tooltip;
  if (params.icon) {
    buttonStyleType += ` h5p-theme-${params.icon}`;
    tooltip = params.tooltip ?? params.label;
  }
  const button = createElement('button', {
    innerHTML: params.label ? `<span class="h5p-theme-label">${params.label}</span>` : '',
    ariaLabel: parseString(params.ariaLabel ?? params.label),
    classList: params.classes ? `${buttonStyleType} ${params.classes}` : buttonStyleType,
    onclick: params.onClick,
    type: params.buttonType ?? 'button',
    disabled: params.disabled ?? false
  });
  if (tooltip) {
    H5P.Tooltip(button, {
      text: tooltip,
      position: params.tooltipPosition ?? 'top'
    });
  }
  if (params.icon) {
    IconOnlyObserver.observe(button);
  }
  return button;
}
const IconOnlyObserver = new ResizeObserver(debounce(entries => {
  for (const entry of entries) {
    const button = entry.target;
    if (!button.isConnected || button.matches(':hover')) {
      continue;
    }
    const label = button.querySelector('.h5p-theme-label');
    const lineCount = computeLineCount(label);
    if (!lineCount) {
      continue;
    }
    const ratio = computeWidthRatio(label, button);
    const shouldHide = lineCount > MAX_LABEL_LINE_COUNT || ratio > MAX_LABEL_WIDTH_RATIO;

    // For visual consistency, label of related buttons should be hidden as well if one is hidden
    const parent = button.parentElement;
    for (const child of parent.children) {
      if (!(child instanceof HTMLButtonElement) || !child.isConnected) {
        continue;
      }
      child.classList.toggle('icon-only', shouldHide);
    }
  }
}));
/* harmony default export */ const h5p_button = (Button);
;// ./src/components/h5p-cover-page.js




/**
 * @typedef {
 *   'check' |
 *   'retry' |
 *   'done' |
 *   'show-results' |
 *   'book' |
 *   'flip' |
 *   'next' |
 *   'previous'
 * } CoverPageIcon
 */

/**
 * @typedef CoverPageParams
 * @type {object}
 * @property {string} title The title for the cover page
 * @property {[string]} description The description or sub-title of the content
 * @property {[string]} img The url to the image
 * @property {[string]} imgAlt The alt text for the image
 * @property {[boolean]} useMediaContainer Add a container instead of an img
 *    so the consumer can attach it themselves
 * @property {string} buttonLabel The label of the button
 * @property {function} buttonOnClick The function to trigger when clicking the button
 * @property {[CoverPageIcon]} icon The name of the icon to use for the button and above the title
 */

/**
 * Create a themed, responsive cover page
 * @param {CoverPageParams} params A set of parameters to configure the CoverPage component
 * @returns {HTMLElement} The cover page element
 */
function CoverPage(params) {
  let coverPageClasses = 'h5p-theme-cover-page';
  if (params.useMediaContainer || params.img) {
    coverPageClasses += ' h5p-theme-cover-page-with-image';
  }
  const coverPage = createElement('div', {
    classList: coverPageClasses
  });
  coverPage.appendChild(createElement('div', {
    classList: 'h5p-theme-pattern-container',
    innerHTML: '<div class="h5p-theme-pattern"></div>'
  }));
  if (params.useMediaContainer) {
    coverPage.appendChild(createElement('div', {
      classList: 'h5p-theme-cover-img'
    }));
  } else if (params.img) {
    coverPage.appendChild(createElement('img', {
      src: params.img,
      alt: params.imgAlt ?? '',
      classList: 'h5p-theme-cover-img'
    }));
  }
  const detailContainer = createElement('div', {
    classList: 'h5p-theme-cover-details'
  });
  if (params.icon) {
    detailContainer.appendChild(createElement('span', {
      classList: `h5p-theme-cover-icon h5p-theme-${params.icon}`,
      ariaHidden: true
    }));
  }
  detailContainer.appendChild(createElement('h2', {
    textContent: params.title
  }));
  if (params.description) {
    detailContainer.appendChild(createElement('p', {
      classList: 'h5p-theme-cover-description',
      innerHTML: params.description
    }));
  }
  detailContainer.appendChild(h5p_button({
    label: params.buttonLabel,
    icon: params.icon,
    onClick: params.buttonOnClick
  }));
  coverPage.appendChild(detailContainer);
  return coverPage;
}
/* harmony default export */ const h5p_cover_page = (CoverPage);
;// ./src/components/h5p-draggable.js



/**
 * @typedef DraggableParams
 * @type {object}
 * @property {string} label A label for the draggable element
 * @property {HTMLElement} [dom]
 *    A DOM element to use as the draggable element Label will be used as fallback
 * @property {number} [tabIndex] Tabindex to use on the draggable element (default 0)
 * @property {boolean} [ariaGrabbed] Initialize the grabbed state on the draggable (default false)
 * @property {boolean} [hasHandle] A boolean determining if the draggable has visual handles or not
 * @property {function} handleRevert A callback function to handle revert
 * @property {function} handleDragEvent A callback function for the drag event
 * @property {function} handleDragStartEvent A callback function for the dragstart event
 * @property {function} handleDragStopEvent A callback function for the dragend event
 */

/**
 * Create a themed, Draggable element
 * @param {DraggableParams} params A set of parameters to configure the Draggable component
 * @returns {HTMLElement} The Draggable element
 */
function Draggable(params) {
  let classes = 'h5p-draggable';
  if (params.hasHandle) {
    classes += ' h5p-draggable--has-handle';
  }
  if (params.statusChangesBackground) {
    classes += ' h5p-draggable--background-status';
  }
  if (params.pointsAndStatus) {
    classes += ' h5p-draggable--points-and-status';
  }
  const setContent = ({
    dom,
    label
  }) => {
    draggable.innerHTML = '';
    if (dom) {
      draggable.append(dom);
    } else {
      draggable.innerHTML = `<span>${label}</span><span class="h5p-hidden-read"></span>`;
    }
  };
  const draggable = createElement('div', {
    classList: classes,
    role: 'button',
    tabIndex: params.tabIndex ?? 0
  });
  setContent({
    dom: params.dom,
    label: params.label
  });

  // Have to set it like this, because it cannot be set with createElement
  draggable.setAttribute('aria-grabbed', params.ariaGrabbed ?? false);

  // Use jQuery draggable (for now)
  H5P.jQuery(draggable).draggable({
    revert: params.handleRevert,
    drag: params.handleDragEvent,
    start: params.handleDragStartEvent,
    stop: params.handleDragStopEvent,
    containment: params.containment
  });

  /**
   * Set opacity of element content
   * @param {number} value Opacity value between 0 and 100
   */
  const setContentOpacity = value => {
    const sanitizedValue = Math.max(0, Math.min(Number(value) ?? 100, 100)) / 100;
    draggable.style.setProperty('--content-opacity', sanitizedValue);
  };
  const setOpacity = value => {
    const sanitizedValue = Math.max(0, Math.min(Number(value) ?? 100, 100)) / 100;
    draggable.style.setProperty('--opacity', sanitizedValue);
  };
  const setDragHandleVisibility = value => {
    draggable.classList.toggle('h5p-draggable--has-handle', value);
  };
  const getBorderWidth = () => {
    const computedStyle = window.getComputedStyle(draggable);
    return computedStyle.getPropertyValue('--border-width');
  };
  draggable.setContentOpacity = setContentOpacity;
  draggable.setOpacity = setOpacity;
  draggable.getBorderWidth = getBorderWidth;
  draggable.setContent = setContent;
  draggable.setDragHandleVisibility = setDragHandleVisibility;
  return draggable;
}
/* harmony default export */ const h5p_draggable = (Draggable);
;// ./src/components/h5p-dropzone.js



/**
 * @typedef {'fit' | 'intersect' | 'pointer' | 'touch'} DropzoneTolerance
 * @typedef {'inline' | 'area'} DropzoneVariant
 */

/**
 * @typedef DropzoneParams
 * @type {object}
 * @property {string} role Role for the dropzone
 * @property {string} ariaLabel A label for the dropzone element
 * @property {number} [index]
 *    An index to track which dropzone this element is in a set Defaults to -1
 * @property {boolean} ariaDisabled If the dropzone should be aria disabled
 * @property {string} [classes] Extra classes to be added to the dropzone
 * @property {string} [containerClasses] Extra classes to be added to the container of the dropzone
 * @property {number} [tabIndex] Tabindex to use on the dropzone element (default -1)
 * @property {boolean} [backgroundOpacity] The level of opacity on the dropzone (0-100)
 * @property {DropzoneVariant} [variant] The type of dropzone to use. Default is 'inline'
 * @property {DropzoneTolerance} tolerance
 *    Specifies which mode to use for testing whether draggable is hovering over a droppable
 * @property {string} [areaLabel] A label used for a dropzone area
 * @property {function} handleAcceptEvent A function for jquery-droppable accept option
 * @property {function} handleDropEvent A callback function for the drop event
 * @property {function} handleDropOutEvent A callback function for the out event
 * @property {function} handleDropOverEvent A callback function for the over event
 */

/**
 * Create a themed, Dropzone element
 * @param {DropzoneParams} params A set of parameters to configure the Dropzone component
 * @returns {HTMLElement} The dropzone element
 */
function Dropzone(params) {
  const classList = ['h5p-dropzone', params.variant === 'area' ? 'h5p-dropzone--area' : 'h5p-dropzone--inline'];
  if (typeof params.containerClasses === 'string') {
    classList.push(params.containerClasses);
  }
  if (params.backgroundOpacity === 0) {
    classList.push('h5p-dropzone--transparent-background');
  } else if (params.backgroundOpacity === 100) {
    classList.push('h5p-dropzone--opaque-background');
  }
  const options = {
    classList: classList.join(' '),
    role: params.role,
    ariaDisabled: params.ariaDisabled
  };
  const dropzoneContainer = createElement('div', options);
  if (params.variant === 'area' && params.areaLabel) {
    const areaLabel = createElement('div', {
      classList: 'h5p-dropzone_label'
    });
    areaLabel.innerHTML = params.areaLabel;
    dropzoneContainer.appendChild(areaLabel);
  }
  const $dropzone = H5P.jQuery('<div/>', {
    'aria-dropeffect': 'none',
    'aria-label': params.ariaLabel,
    tabindex: params.tabIndex ?? -1,
    class: params.classes ? params.classes : ''
  }).appendTo(dropzoneContainer).droppable({
    activeClass: 'h5p-dropzone--active',
    tolerance: params.tolerance,
    accept: params.handleAcceptEvent,
    over: (event, ui) => {
      dropzone.classList.add('h5p-dropzone--hover');
      params.handleDropOverEvent?.(event, ui);
    },
    out: (event, ui) => {
      dropzone.classList.remove('h5p-dropzone--hover');
      params.handleDropOutEvent?.(event, ui);
    },
    drop: (event, ui) => {
      dropzone.classList.remove('h5p-dropzone--hover');
      params.handleDropEvent?.(event, ui, params.index ?? -1);
    }
  });
  const dropzone = $dropzone.get(0);
  return dropzoneContainer;
}
/* harmony default export */ const h5p_dropzone = (Dropzone);
;// ./src/components/h5p-progress-bar.js



/**
 * @typedef ProgressBarParams
 * @type {object}
 * @property {number} [index] The current position in the navigation (default: 0)
 * @property {number} [progressLength] The number of "items" we can navigate through (default: 1)
 * @property {number} [ariaValueMax] The max value of the slider (default: 100)
 * @property {number} [ariaValueMin] The min value of the slider (default: 0)
 * @property {number} [ariaValueNow] The current/initial value of the slider (default: 0)
 */

/**
 * Creates a progress bar.
 * @param {ProgressBarParams} params A set of parameters to configure ProgressBar
 * @returns {HTMLElement} The ProgressBar element.
 */
function ProgressBar(params = {}) {
  const progressLength = params.progressLength ?? 1;
  let index = params.index ?? 0;
  const progressBar = createElement('div', {
    classList: 'h5p-visual-progress',
    role: 'progressbar',
    ariaValueMax: params.ariaValueMax ?? 100,
    ariaValueMin: params.ariaValueMin ?? 0,
    ariaValueNow: params.ariaValueNow ?? 0
  });
  const progressBarInner = createElement('div', {
    classList: 'h5p-visual-progress-inner'
  });
  progressBar.appendChild(progressBarInner);
  const updateProgressBar = newIndex => {
    index = newIndex;
    progressBar.setAttribute('aria-valuenow', ((newIndex + 1) / progressLength * 100).toFixed(2));
    progressBarInner.style.width = `${(newIndex + 1) / progressLength * 100}%`;
  };
  updateProgressBar(index);
  progressBar.updateProgressBar = updateProgressBar;
  return progressBar;
}
/* harmony default export */ const h5p_progress_bar = (ProgressBar);
;// ./src/components/h5p-progress-dots.js


/**
 * @typedef ProgressDots
 * @type {object}
 * @property {string} ariaLabel A label for screen reader users when navigating to a dot
 * @property {[number]} tabIndex Initial tabIndex for a dot
 */

/**
 * @typedef ProgressDotsTexts
 * @type {object}
 * @property {string} jumpToQuestion
 * @property {string} answeredText
 * @property {string} unansweredText
 * @property {string} currentQuestionText
 */

/**
 * @typedef ProgressDotsParams
 * @type {object}
 * @property {[number]} index The current position in the navigation
 * @property {ProgressDots[]} dots Array of dots to process
 * @property {ProgressDotsTexts} texts A collection of translatable strings
 * @property {[function]} handleProgressDotClick A callback function when a dot is clicked
 */

/**
 * Creates navigational dots
 * @param {ProgressDotsParams} params A set of parameters to configure ProgressDots
 * @returns {HTMLElement} The ProgressDots element
 */
function ProgressDots(params = {}) {
  const progressLength = params.dots.length;
  let activeIndex = params.index ?? 0;
  const progressDotElements = [];
  const dotsContainer = createElement('ul', {
    className: 'h5p-progress-dots-container'
  });
  const onProgressDotClick = event => {
    event.preventDefault();
    const newIndex = Number(event.target.getAttribute('data-index'));
    toggleCurrentDot(newIndex);
    params.handleProgressDotClick?.(event);
  };
  const onKeyDown = event => {
    switch (event.code) {
      case 'Enter':
      case 'Space':
        onProgressDotClick(event);
        break;
      case 'ArrowLeft':
      case 'ArrowUp':
        // Go to previous dot
        setActiveDot(activeIndex - 1);
        break;
      case 'ArrowRight':
      case 'ArrowDown':
        // Go to next dot
        setActiveDot(activeIndex + 1);
        break;
      default:
        break;
    }
  };
  const hasOneFocusableDot = params.dots.some(dot => dot.tabIndex >= 0);
  params.dots.forEach((dot, i) => {
    const item = createElement('li', {
      className: 'h5p-progress-item'
    });
    // We need to ensure that we can keyboard navigate to at least one of the dots
    let tabIndex;
    if (hasOneFocusableDot) {
      tabIndex = dot.tabIndex ?? -1;
    } else if (i === 0) {
      tabIndex = 0;
    } else {
      tabIndex = -1;
    }
    const progressDot = createElement('a', {
      href: '#',
      className: `h5p-progress-dot unanswered ${tabIndex >= 0 ? 'current' : ''}`,
      ariaLabel: dot.ariaLabel,
      tabIndex,
      onclick: onProgressDotClick,
      onkeydown: onKeyDown
    });
    progressDot.setAttribute('data-index', i);
    item.appendChild(progressDot);
    dotsContainer.appendChild(item);
    progressDotElements.push(progressDot);
  });
  const setActiveDot = (newIndex, placeFocus = true) => {
    if (newIndex < 0 || newIndex >= progressLength) {
      return;
    }
    activeIndex = newIndex;
    progressDotElements.forEach((el, i) => {
      el.setAttribute('tabIndex', activeIndex === i ? 0 : -1);
    });
    if (placeFocus) {
      progressDotElements[activeIndex].focus();
    }
  };
  const toggleCurrentDot = newIndex => {
    const {
      texts
    } = params;
    progressDotElements.forEach((el, i) => {
      el.setAttribute('tabIndex', activeIndex === i ? 0 : -1);
      const isCurrent = i === newIndex;
      let label = texts.jumpToQuestion.replace('%d', (newIndex + 1).toString()).replace('%total', progressDotElements.length);
      if (!isCurrent) {
        const isAnswered = el.classList.contains('answered');
        label += `, ${isAnswered ? texts.answeredText : texts.unansweredText}`;
      } else {
        label += `, ${texts.currentQuestionText}`;
      }
      el.classList.toggle('current', isCurrent);
      el.setAttribute('aria-label', label);
    });
  };
  const toggleFilledDot = (filledIndex, isFilled) => {
    const label = `${params.texts.jumpToQuestion.replace('%d', (filledIndex + 1).toString()).replace('%total', progressDotElements.length)}, ${isFilled ? params.texts.answeredText : params.texts.unansweredText}`;
    progressDotElements[filledIndex].classList.toggle('unanswered', !isFilled);
    progressDotElements[filledIndex].classList.toggle('answered', isFilled);
    progressDotElements[filledIndex].setAttribute('aria-label', label);
  };
  dotsContainer.setActiveDot = setActiveDot;
  dotsContainer.toggleFilledDot = toggleFilledDot;
  dotsContainer.toggleCurrentDot = toggleCurrentDot;
  return dotsContainer;
}
/* harmony default export */ const h5p_progress_dots = (ProgressDots);
;// ./src/components/h5p-navigation.js
/* eslint-disable no-param-reassign */
/* eslint-disable no-nested-ternary */






/**
 * @typedef NavigationTexts
 * @type {object}
 * @property {string} previousButton
 * @property {string} nextButton
 * @property {string} lastButton
 * @property {[string]} previousButtonAria
 * @property {[string]} nextButtonAria
 * @property {[string]} lastButtonAria
 * @property {[string]} previousTooltip
 * @property {[string]} nextTooltip
 * @property {[string]} lastTooltip
 * @property {[string]} currentTooltip
 * @property {[string]} totalTooltip
 * The items below are used by ProgressDots
 * @property {string} jumpToQuestion
 * @property {string} answeredText
 * @property {string} unansweredText
 * The item below is used by ProgressText
 * @property {string} textualProgress
 */

/**
 * @typedef {'3-split' | '2-split-next' | '2-split-spread'} NavigationVariant
 * @typedef {'bar' | 'dots' | 'text'} NavigationProgressType
 */

/**
 * @typedef NavigationParams
 * @type {object}
 * @property {number} index The current position in the navigation
 * @property {number} navigationLength The number of "items" we can navigate through
 * @property {[NavigationVariant]} variant
 *    The type of grid layout for the navigation (3split is default)
 * @property {[NavigationTexts]} texts
 *    Translations stuff. @todo, should H5P.Component maintain own translations?
 * @property {[string]} className Extra css classes to be applied on the navigation element
 * @property {[function]} handlePrevious
 *    A function that enables the previous button and triggers when it has been clicked
 * @property {[function]} handleNext
 *    A function that enables the next button and triggers when it has been clicked
 * @property {[function]} handleLast
 *    A function that enables the "last" button and triggers when it has been clicked
 *    Typically a "submit" or "show results" button
 * @property {[NavigationProgressType]} progressType
 *    Can show a progress bar, dot navigation or textual progress
 * @property {[Array]} dots
 *    If progressType==='dots', the dots array is required
 *    Each dot has tabIndex and ariaLabel property
 * @property {[function]} handleProgressDotClick
 *    A function that is called when the user clicks the on a "dot". Optional
 * @property {[object]} options
 * @property {[boolean]} options.disableBackwardsNavigation
 *    If backwards navigation should be disabled or not
 * @property {[boolean]} showDisabledButtons
 *    If true, buttons will be disabled instead of hidden when not usable
 *  @property {[Array]} titles
 *    Array of titles for each page/chapter, used when progressType is 'text'
 */

/**
 * Create DOM elements from text with placeholders
 * @param {string} text - Text containing placeholders like @current, @total
 * @param {object} replacements - Object mapping placeholder names to replacement functions
 * @returns {[Node]} Array of DOM nodes (text nodes and elements)
 */
function createElementsFromPlaceholders(text, replacements) {
  const placeholders = Object.keys(replacements);
  const regExp = new RegExp(`(${placeholders.map(p => p.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('|')})`, 'g');
  return text.split(regExp).filter(part => part !== '').map(part => replacements[part] ? replacements[part]() : document.createTextNode(part));
}

/**
 * Create a span element with optional tooltip
 * @param {string} className - CSS class name for the span
 * @param {string|number} content - Text content for the span
 * @param {string} [tooltipText] - Optional tooltip text
 * @returns {HTMLElement} The span element
 */
function createProgressSpan(className, content, tooltipText) {
  const span = createElement('span', {
    classList: className,
    innerText: content
  });
  if (tooltipText) {
    H5P.Tooltip(span, {
      text: tooltipText,
      position: 'top'
    });
  }
  return span;
}

/**
 * Update progress text element with new current/total values
 * @param {HTMLElement} progressText - Existing progress text element to update
 * @param {string} textualProgress - Text template with @current and @total placeholders
 * @param {number} currentIndex - Current index (0-based)
 * @param {number} navigationLength - Total number of items
 * @param {object} texts - Text configuration object
 * @param {string} [params.texts.currentTooltip] - Tooltip for current index
 * @param {string} [params.texts.totalTooltip] - Tooltip for total count*
 */
// eslint-disable-next-line max-len
function updateProgressText(progressText, textualProgress, currentIndex, navigationLength, texts = {}) {
  // Clear existing content
  progressText.innerHTML = '';

  // Create new content
  const domParts = createElementsFromPlaceholders(textualProgress, {
    '@current': () => createProgressSpan('progress-current', currentIndex + 1, texts.currentTooltip),
    '@total': () => createProgressSpan('progress-last', navigationLength, texts.totalTooltip)
  });
  domParts.forEach(part => progressText.appendChild(part));
}

/**
 * Create a progress text element with current/total placeholders
 * @param {object} params - Parameters for creating progress text
 * @param {string} params.textualProgress - Text template with @current and @total placeholders
 * @param {number} params.currentIndex - Current index (0-based)
 * @param {number} params.navigationLength - Total number of items
 * @param {object} params.texts - Text configuration object
 * @param {string} [params.texts.currentTooltip] - Tooltip for current index
 * @param {string} [params.texts.totalTooltip] - Tooltip for total count
 * @returns {HTMLElement} The complete progressText element
 */
function createProgressText({
  textualProgress,
  currentIndex,
  navigationLength,
  texts = {}
}) {
  const progressText = createElement('div', {
    classList: 'progress-text'
  });
  updateProgressText(progressText, textualProgress, currentIndex, navigationLength, texts);
  return progressText;
}

/**
 * Create a navigation component, with optional progress components.
 * @param {NavigationParams} params A set of parameters to configure the Navigation component
 * @returns {HTMLElement} The navigation element
 */
function Navigation(params = {}) {
  let progressBar;
  let dotsNavigation;
  let progressText;
  let title;
  let prevButton;
  let nextButton;
  let lastButton;
  let canShowLast = false;
  let index = params.index ?? 0;
  let className = 'h5p-navigation';
  if (params.variant === '2-split-spread') {
    className += ' h5p-navigation--2-split-spread';
  } else if (params.variant === '2-split-next') {
    className += ' h5p-navigation--2-split-next';
  } else {
    className += ' h5p-navigation--3-split';
  }
  const container = createElement('nav', {
    classList: `${className} ${params.className ?? ''}`,
    role: 'navigation'
  });
  if (params.handlePrevious) {
    const prevClassList = 'h5p-theme-previous';
    prevButton = h5p_button({
      styleType: 'nav',
      label: params?.texts?.previousButton ?? 'Previous',
      ariaLabel: params?.texts.previousButtonAria,
      tooltip: params?.texts.previousTooltip,
      icon: 'previous',
      classes:
      // eslint-disable-next-line no-nested-ternary
      index === 0 ? params.showDisabledButtons ? `${prevClassList} h5p-disabled` : `${prevClassList} h5p-visibility-hidden` : prevClassList,
      disabled: params.showDisabledButtons && index === 0,
      onClick: event => {
        if (params.handlePrevious(event) !== false) {
          previous();
        }
      }
    });
    container.appendChild(prevButton);
  }
  if (params.progressType === 'bar') {
    progressBar = h5p_progress_bar({
      index,
      progressLength: params.navigationLength
    });
    container.appendChild(progressBar);
  } else if (params.progressType === 'dots') {
    dotsNavigation = h5p_progress_dots({
      dots: params.dots,
      texts: params.texts ?? {},
      handleProgressDotClick: event => {
        index = Number(event.target.getAttribute('data-index'));
        params.handleProgressDotClick?.(event, index);
      }
    });
    container.appendChild(dotsNavigation);
  } else if (params.progressType === 'text') {
    const progressContainer = createElement('div', {
      classList: 'progress-container h5p-theme-progress'
    });
    progressText = createProgressText({
      textualProgress: params.texts.textualProgress,
      currentIndex: index,
      navigationLength: params.navigationLength,
      texts: params.texts
    });
    progressContainer.appendChild(progressText);

    // Page chapter title used in IB
    if (params.titles && params.titles.length > 0) {
      title = createElement('h1', {
        classList: 'title'
      });
      title.textContent = params.titles[index] || '';
      const progressWrapper = createElement('div', {
        classList: 'progress-wrapper'
      });
      progressWrapper.appendChild(progressContainer);
      progressWrapper.appendChild(title);
      container.appendChild(progressWrapper);
    } else {
      container.appendChild(progressContainer);
    }
  }
  if (params.handleNext) {
    const nextClassList = 'h5p-theme-next';
    nextButton = h5p_button({
      styleType: 'nav',
      label: params?.texts?.nextButton ?? 'Next',
      ariaLabel: params?.texts.nextButtonAria,
      tooltip: params?.texts.nextTooltip,
      icon: 'next',
      classes: index === params.navigationLength - 1 ? params.showDisabledButtons ? `${nextClassList} h5p-disabled` : `${nextClassList} h5p-visibility-hidden` : nextClassList,
      disabled: params.showDisabledButtons && index === params.navigationLength - 1,
      onClick: event => {
        if (params.handleNext(event) !== false) {
          next();
        }
      }
    });
    container.appendChild(nextButton);
  }
  if (params.handleLast) {
    lastButton = h5p_button({
      styleType: 'primary',
      label: params?.texts?.lastButton ?? 'Submit',
      ariaLabel: params?.texts.lastButtonAria,
      tooltip: params?.texts.lastTooltip,
      icon: 'show-results',
      classes: 'h5p-visibility-hidden',
      onClick: event => {
        next();
        params.handleLast(event);
      }
    });
    container.appendChild(lastButton);
  }
  const calculateButtonVisibility = () => {
    if (params.showDisabledButtons) {
      // Disable/enable buttons instead of hiding them
      if (prevButton) {
        prevButton.toggleAttribute('disabled', index === 0);
        prevButton.classList.toggle('h5p-disabled', index === 0);
      }
      if (nextButton) {
        const isLastPage = index >= params.navigationLength - 1;
        nextButton.toggleAttribute('disabled', isLastPage);
        nextButton.classList.toggle('h5p-disabled', isLastPage);

        // Last button still uses visibility logic
        lastButton?.classList.toggle('h5p-visibility-hidden', !canShowLast || !isLastPage);
      }
    } else {
      // Original behavior - hide/show buttons
      if (prevButton && index === 0) {
        prevButton.classList.add('h5p-visibility-hidden');
      } else if (prevButton && index > 0) {
        prevButton.classList.remove('h5p-visibility-hidden');
      }
      if (nextButton && index >= params.navigationLength - 1) {
        nextButton.classList.add('h5p-visibility-hidden');
        lastButton?.classList.toggle('h5p-visibility-hidden', !canShowLast);
      } else if (nextButton && index < params.navigationLength - 1) {
        nextButton.classList.remove('h5p-visibility-hidden');
        lastButton?.classList.add('h5p-visibility-hidden');
      }
    }
  };
  const setCanShowLast = canShow => {
    canShowLast = canShow;
    calculateButtonVisibility();
  };
  const setCurrentIndex = newIndex => {
    index = newIndex;
    if (title && params.titles && params.titles[index]) {
      title.textContent = params.titles[index];
    }
    if (progressBar) {
      progressBar.updateProgressBar(index);
    } else if (progressText) {
      updateProgressText(progressText, params.texts.textualProgress, index, params.navigationLength, params.texts);
    } else if (dotsNavigation) {
      dotsNavigation.toggleCurrentDot(index);
    }
    calculateButtonVisibility();
  };
  const previous = () => {
    setCurrentIndex(index - 1);
  };
  const next = () => {
    setCurrentIndex(index + 1);
  };
  const setNavigationLength = navigationLength => {
    if (typeof navigationLength !== 'number' || navigationLength < 0) {
      throw new Error('Invalid navigation length');
    }
    params.navigationLength = navigationLength;
  };
  container.setCurrentIndex = setCurrentIndex;
  container.setNavigationLength = setNavigationLength;
  container.previous = previous;
  container.next = next;
  container.setCanShowLast = setCanShowLast;
  container.progressBar = progressBar;
  container.progressDots = dotsNavigation;
  return container;
}
/* harmony default export */ const h5p_navigation = (Navigation);
;// ./src/components/h5p-placeholder-img.js



/**
 * Returns true if the string parses and contains at least one valid <svg> element
 * @param {string} value
 */
function containsSvgElement(value) {
  if (typeof value !== 'string') {
    return false;
  }
  const input = value.trim();
  if (!input.includes('<svg')) {
    return false;
  }
  const xmlDoc = new DOMParser().parseFromString(input, 'image/svg+xml');
  const hasParserError = xmlDoc.getElementsByTagName('parsererror').length > 0;
  if (hasParserError) {
    return false;
  }
  return xmlDoc.getElementsByTagName('svg').length > 0;
}

/**
 *  Create a themed placeholder svg
 *
 *  The function accepts either:
 *  - A string containing an <svg> element (raw SVG or XML that includes SVG)
 *  - A key that matches one of the predefined placeholder SVGs in 'placeholderSVGs'
 *  - If no valid SVG or key is provided, the 'default' placeholder is used.
 *
 * @param {string} [arg]
 * A string containing an <svg> element or a key referring to an entry in 'placeholderSVGs'
 * @returns {HTMLElement} The placeholder image element
 */
function PlaceholderImg(arg) {
  const svg = containsSvgElement(arg) ? arg : placeholderSVGs[arg] ?? placeholderSVGs.default;
  return createElement('div', {
    classList: 'h5p-theme-placeholder-img',
    innerHTML: svg
  });
}

// Can't use img, or object with a path since we need to access variables outside the svg
const placeholderSVGs = {
  default: `
    <svg version="1.1" xmlns="http://www.w3.org/2000/svg" 
        xmlns:xlink="http://www.w3.org/1999/xlink" x="0px" y="0px" 
        viewBox="0 0 500 500" style="enable-background:new 0 0 500 500;" xml:space="preserve">
      <style type="text/css">
        .st0{fill:var(--h5p-theme-alternative-darker);}
        .st1{fill:var(--h5p-theme-alternative-base);}
        .st2{fill:var(--h5p-theme-alternative-dark);}
        .st3{fill:var(--h5p-theme-ui-base);}
      </style>
      <g>
        <path class="st0" d="M369.3,388.9c-0.5,0.2-1,0.3-1.5,0.4l-257.8,36c-2.3,0.3-4.7-0.3-6.6-1.7c-1.9-1.4-3.1-3.5-3.4-5.8L64,159.9c-0.7-4.8,2.7-9.3,7.5-10l257.8-36c2.3-0.3,4.7,0.3,6.6,1.7c1.9,1.4,3.1,3.5,3.4,5.8l36,257.8C375.9,383.5,373.3,387.6,369.3,388.9z"/>
        <rect x="113.8" y="103" transform="matrix(0.1337 -0.991 0.991 0.1337 -21.8517 475.0013)" class="st1" width="294" height="294"/>
        <polygon class="st2" points="244.1,396.1 252.1,337.1 181.3,279.3 102.9,320.5 95.4,376"/>
        <polygon class="st0" points="100.4,338.9 193.4,289.9 181.6,279.1 103,319.8"/>
        <path class="st0" d="M172,89.7c12,47.4,51.6,85.1,103.1,92.1c51.4,6.9,99.7-18.9,123.8-61.4L172,89.7z"/>
        <g>
          <g>
            <path class="st2" d="M300.9,107.1l-88.3,47c17.2,14.4,38.6,24.3,62.6,27.5c51.4,6.9,99.6-18.8,123.7-61.4L300.9,107.1z"/>
          </g>
        </g>
        <polygon class="st2" points="401.1,309 351.6,268.5 136.9,381.6 386.8,415.3"/>
        <polygon class="st0" points="170.9,386.2 367.4,282.4 351.9,268.3 134.1,381.2"/>
        <path class="st3" d="M387.3,425.3c-0.6,0-1.2,0-1.8-0.1L94.1,385.9c-2.6-0.4-5-1.7-6.6-3.8c-1.6-2.1-2.3-4.8-2-7.4l39.3-291.4c0.7-5.5,5.8-9.3,11.2-8.6l291.4,39.3c2.6,0.4,5,1.7,6.6,3.8c1.6,2.1,2.3,4.8,2,7.4l-39.3,291.4C396,421.5,392,425.1,387.3,425.3zM106.7,367.5l271.5,36.6l36.6-271.5L143.3,95.9L106.7,367.5z"/>
      </g>
    </svg>
    `,
  h5pImageDefault: `
    <svg class="h5p-image-placeholder-svg" xmlns="http://www.w3.org/2000/svg" version="1.1" viewBox="0 0 903 459" preserveAspectRatio="xMidYMid slice">
      <defs>
        <style>
          .cls-1 {fill: var(--h5p-theme-alternative-darker);}
          .cls-2 {fill: var(--h5p-theme-alternative-dark);}
          .cls-3 {fill: var(--h5p-theme-alternative-base);}
        </style>
      </defs>
      <g>
        <g>
          <rect class="cls-3" x="1" y="0" width="903.1" height="459.1"/>
          <polygon class="cls-2" points="527.5 459.5 527.5 334.1 364.8 234 48.1 459.5 527.5 459.5"/>
          <polygon class="cls-2" points="904.2 246 732.2 142.6 287.1 459.8 904.2 459.8 904.2 246"/>
          <polygon class="cls-2" points="394.7 459.5 106.3 254 .1 332.4 .1 459.5 394.7 459.5"/>
          <polygon class="cls-1" points="-.3 366.9 133.8 274.2 105.1 255.7 -.3 332.9 -.3 366.9"/>
          <polygon class="cls-1" points="370.5 459.2 771.6 168.7 732.2 142.6 292 459.2 370.5 459.2"/>
          <polygon class="cls-1" points="102.8 459.5 392.8 252.6 365.3 233.5 43.6 459.5 102.8 459.5"/>
          <path class="cls-1" d="M43.3.4c30.1,78,105.7,133.3,194.3,133.3S401.8,78.3,431.8.4H43.3Z"/>
          <path class="cls-2" d="M267.4.4L126.7,101.6c32.1,20.3,70.1,32,110.9,32,88.6,0,164.2-55.3,194.3-133.3h-164.5Z"/>
        </g>
      </g>
    </svg>
    `
};
/* harmony default export */ const h5p_placeholder_img = (PlaceholderImg);
;// ./src/components/h5p-result-screen.js


/**
 * @typedef ResultQuestion
 * @type {object}
 * @property {[string]} imgUrl The url to an image to display before the question
 * @property {[boolean]} useDefaultImg Use a default image. Will be overwritten by imgUrl
 * @property {string} title The textual description of the question
 * @property {string} points The score of the question
 * @property {[boolean]} isCorrect If the answer is correct (Some content types are more lenient)
 * @property {[string]} userAnswer What the user answered
 * @property {[string]} correctAnswer The correct answer
 * @property {[string]} correctAnswerPrepend The label before the correct answer
 */

/**
 * @typedef ResultQuestionGroup
 * @type {object}
 * @property {[string[]]} listHeaders The table headers
 * @property {ResultQuestion[]} questions The list of tasks to be summarized
 */

/**
 * @typedef ResultScreenParams
 * @type {object}
 * @property {string} header The main header of the result screen
 * @property {string} scoreHeader The header detailing the total score
 * @property {ResultQuestionGroup[]} questionGroups The groups of questions
 */

/**
 * Create a result screen, summing up the tasks of the content and the scores achieved
 * @param {ResultScreenParams} params A set of parameters to configure the ResultScreen component
 * @returns {HTMLElement} The result screen element
 */
function ResultScreen(params) {
  // Create main wrapper
  const resultScreen = createElement('div', {
    classList: 'h5p-theme-result-screen'
  });

  // Create header banner
  const header = createElement('div', {
    classList: 'h5p-theme-results-banner'
  });
  header.appendChild(createElement('div', {
    classList: 'h5p-theme-pattern'
  }));
  header.appendChild(createElement('div', {
    classList: 'h5p-theme-results-title',
    textContent: params.header
  }));
  header.appendChild(createElement('div', {
    classList: 'h5p-theme-results-score',
    innerHTML: params.scoreHeader
  }));
  resultScreen.append(header);

  // Create the summary table
  params.questionGroups.forEach(group => {
    const groupContainer = createElement('div', {
      classList: 'h5p-theme-results-list-container'
    });
    if (group.listHeaders) {
      const listHeaders = createElement('div', {
        classList: 'h5p-theme-results-list-heading'
      });
      group.listHeaders.forEach(title => {
        listHeaders.appendChild(createElement('div', {
          classList: 'heading-item',
          textContent: title
        }));
      });
      groupContainer.appendChild(listHeaders);
    }
    const resultList = createElement('ul', {
      classList: 'h5p-theme-results-list'
    });
    group.questions.forEach(question => {
      resultList.appendChild(createQuestion(question));
    });
    groupContainer.appendChild(resultList);
    resultScreen.appendChild(groupContainer);
  });
  return resultScreen;
}
const createQuestion = question => {
  const listItem = createElement('li', {
    classList: 'h5p-theme-results-list-item'
  });
  if (question.imgUrl) {
    listItem.appendChild(createElement('div', {
      classList: 'h5p-theme-results-image'
    }, {
      'background-image': `url("${question.imgUrl}")`
    }));
  } else if (question.useDefaultImg) {
    const imageContainer = createElement('div', {
      classList: 'h5p-theme-results-image'
    });
    imageContainer.appendChild(H5P.Components.PlaceholderImg('h5pImageDefault'));
    listItem.appendChild(imageContainer);
  }
  const questionContainer = createElement('div', {
    classList: 'h5p-theme-results-question-container'
  });
  questionContainer.appendChild(createElement('div', {
    classList: 'h5p-theme-results-question',
    innerHTML: question.title
  }));

  // UserAnswer might be an empty string
  if (typeof question.userAnswer === 'string') {
    const answerContainer = createElement('div', {
      classList: 'h5p-theme-results-answer'
    });
    const answer = createElement('span', {
      classList: 'h5p-theme-results-box-small h5p-theme-results-correct',
      textContent: question.userAnswer
    });
    answerContainer.appendChild(answer);

    // isCorrect defined AND false
    if (question.isCorrect === false) {
      answer.classList.add('h5p-theme-results-incorrect');
      answer.classList.remove('h5p-theme-results-correct');
      if (question.correctAnswer) {
        const solutionContainer = createElement('span', {
          classList: 'h5p-theme-results-solution'
        });
        if (question.correctAnswerPrepend) {
          solutionContainer.appendChild(createElement('span', {
            classList: 'h5p-theme-results-solution-label',
            textContent: question.correctAnswerPrepend
          }));
        }
        solutionContainer.innerHTML += question.correctAnswer;
        answerContainer.appendChild(solutionContainer);
      }
    }
    questionContainer.appendChild(answerContainer);
  }
  listItem.appendChild(questionContainer);
  listItem.appendChild(createElement('div', {
    classList: 'h5p-theme-results-points',
    innerHTML: question.points
  }));
  return listItem;
};
/* harmony default export */ const h5p_result_screen = (ResultScreen);
;// ./src/entries/dist.js











// eslint-disable-next-line no-global-assign
H5P = H5P || {};
H5P.Components = H5P.Components || {};
H5P.Components.CoverPage = h5p_cover_page;
H5P.Components.Button = h5p_button;
H5P.Components.Draggable = h5p_draggable;
H5P.Components.Dropzone = h5p_dropzone;
H5P.Components.Navigation = h5p_navigation;
H5P.Components.PlaceholderImg = h5p_placeholder_img;
H5P.Components.ProgressBar = h5p_progress_bar;
H5P.Components.ProgressDots = h5p_progress_dots;
H5P.Components.ResultScreen = h5p_result_screen;
/******/ })()
;
//# sourceMappingURL=data:application/json;charset=utf-8;base64,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Q2tCO0FBQ1A7QUFDTTtBQUNGO0FBQ0k7QUFDUztBQUNOO0FBQ0U7QUFDQTs7QUFFOUQ7QUFDQXhPLEdBQUcsR0FBR0EsR0FBRyxJQUFJLENBQUMsQ0FBQztBQUNmQSxHQUFHLENBQUN3UCxVQUFVLEdBQUd4UCxHQUFHLENBQUN3UCxVQUFVLElBQUksQ0FBQyxDQUFDO0FBRXJDeFAsR0FBRyxDQUFDd1AsVUFBVSxDQUFDbE8sU0FBUyxHQUFHQSxjQUFTO0FBQ3BDdEIsR0FBRyxDQUFDd1AsVUFBVSxDQUFDelEsTUFBTSxHQUFHQSxVQUFNO0FBQzlCaUIsR0FBRyxDQUFDd1AsVUFBVSxDQUFDbk4sU0FBUyxHQUFHQSxhQUFTO0FBQ3BDckMsR0FBRyxDQUFDd1AsVUFBVSxDQUFDaEwsUUFBUSxHQUFHQSxZQUFRO0FBQ2xDeEUsR0FBRyxDQUFDd1AsVUFBVSxDQUFDbEUsVUFBVSxHQUFHQSxjQUFVO0FBQ3RDdEwsR0FBRyxDQUFDd1AsVUFBVSxDQUFDdEIsY0FBYyxHQUFHQSxtQkFBYztBQUM5Q2xPLEdBQUcsQ0FBQ3dQLFVBQVUsQ0FBQ2pKLFdBQVcsR0FBR0EsZ0JBQVc7QUFDeEN2RyxHQUFHLENBQUN3UCxVQUFVLENBQUN0SSxZQUFZLEdBQUdBLGlCQUFZO0FBQzFDbEgsR0FBRyxDQUFDd1AsVUFBVSxDQUFDaEIsWUFBWSxHQUFHQSxpQkFBWSxDIiwic291cmNlcyI6WyJ3ZWJwYWNrOi8vaDVwLmNvbXBvbmVudHMtMS4wLy4vc3JjL3V0aWxzLmpzIiwid2VicGFjazovL2g1cC5jb21wb25lbnRzLTEuMC8uL3NyYy9jb21wb25lbnRzL2g1cC1idXR0b24uanMiLCJ3ZWJwYWNrOi8vaDVwLmNvbXBvbmVudHMtMS4wLy4vc3JjL2NvbXBvbmVudHMvaDVwLWNvdmVyLXBhZ2UuanMiLCJ3ZWJwYWNrOi8vaDVwLmNvbXBvbmVudHMtMS4wLy4vc3JjL2NvbXBvbmVudHMvaDVwLWRyYWdnYWJsZS5qcyIsIndlYnBhY2s6Ly9oNXAuY29tcG9uZW50cy0xLjAvLi9zcmMvY29tcG9uZW50cy9oNXAtZHJvcHpvbmUuanMiLCJ3ZWJwYWNrOi8vaDVwLmNvbXBvbmVudHMtMS4wLy4vc3JjL2NvbXBvbmVudHMvaDVwLXByb2dyZXNzLWJhci5qcyIsIndlYnBhY2s6Ly9oNXAuY29tcG9uZW50cy0xLjAvLi9zcmMvY29tcG9uZW50cy9oNXAtcHJvZ3Jlc3MtZG90cy5qcyIsIndlYnBhY2s6Ly9oNXAuY29tcG9uZW50cy0xLjAvLi9zcmMvY29tcG9uZW50cy9oNXAtbmF2aWdhdGlvbi5qcyIsIndlYnBhY2s6Ly9oNXAuY29tcG9uZW50cy0xLjAvLi9zcmMvY29tcG9uZW50cy9oNXAtcGxhY2Vob2xkZXItaW1nLmpzIiwid2VicGFjazovL2g1cC5jb21wb25lbnRzLTEuMC8uL3NyYy9jb21wb25lbnRzL2g1cC1yZXN1bHQtc2NyZWVuLmpzIiwid2VicGFjazovL2g1cC5jb21wb25lbnRzLTEuMC8uL3NyYy9lbnRyaWVzL2Rpc3QuanMiXSwic291cmNlc0NvbnRlbnQiOlsiLyoqIEBjb25zdGFudCB7bnVtYmVyfSBERUJPVU5DRV9ERUxBWV9NUyBEZWJvdW5jZSBkZWxheSB0byB1c2UgKi9cbmNvbnN0IERFQk9VTkNFX0RFTEFZX01TID0gNDA7XG5cbi8qKiBAY29uc3RhbnQge251bWJlcn0gREVGQVVMVF9MSU5FX0hFSUdIVCBEZWZhdWx0IGxpbmUgaGVpZ2h0IHdoZW4gaXQgaXMgXCJub3JtYWxcIiAqL1xuY29uc3QgREVGQVVMVF9MSU5FX0hFSUdIVCA9IDEuMjtcblxuLyoqIEBjb25zdGFudCB7bnVtYmVyfSBDTE9TRV9UT19JTlRFR0VSX0VQU0lMT04gRXBzaWxvbiBmb3IgY2xvc2VuZXNzIHRvIGludGVnZXIgKi9cbmNvbnN0IENMT1NFX1RPX0lOVEVHRVJfRVBTSUxPTiA9IDAuMDE7XG5cbi8qKlxuICogU3RyaXBzIGh0bWwgdGFncyBhbmQgY29udmVydHMgc3BlY2lhbCBjaGFyYWN0ZXJzLlxuICogRXhhbXBsZTogXCI8ZGl2Pk1lICZhbXA7IHlvdTwvZGl2PlwiIGlzIGNvbnZlcnRlZCB0byBcIk1lICYgeW91XCIuXG4gKlxuICogQHBhcmFtIHtTdHJpbmd9IHRleHQgVGhlIHRleHQgdG8gYmUgcGFyc2VkXG4gKiBAcmV0dXJucyB7U3RyaW5nfSBUaGUgcGFyc2VkIHRleHRcbiAqL1xuZXhwb3J0IGNvbnN0IHBhcnNlU3RyaW5nID0gKHRleHQpID0+IHtcbiAgaWYgKHRleHQgPT09IG51bGwgfHwgdGV4dCA9PT0gdW5kZWZpbmVkKSB7XG4gICAgcmV0dXJuICcnO1xuICB9XG4gIGNvbnN0IGRpdiA9IGRvY3VtZW50LmNyZWF0ZUVsZW1lbnQoJ2RpdicpO1xuICBkaXYuaW5uZXJIVE1MID0gdGV4dDtcbiAgcmV0dXJuIGRpdi50ZXh0Q29udGVudDtcbn07XG5cbi8qKlxuICogQ3JlYXRlIGFuIEhUTUwgZWxlbWVudCwgYW5kIGFwcGx5IHBvdGVudGlhbCBvcHRpb25zL2Nzc1xuICpcbiAqIEBwYXJhbSB7c3RyaW5nfSB0YWcgVGhlIEhUTUwgdGFnIHRvIGNyZWF0ZVxuICogQHBhcmFtIHtvYmplY3R9IG9wdGlvbnMgT3B0aW9ucyBsaWtlIGNsYXNzTGlzdCwgdGV4dENvbnRlbnQgZXRjLlxuICogQHBhcmFtIHtvYmplY3R9IHN0eWxlIFN0eWxlcy9jc3MgdG8gYXBwbHkgdG8gdGhlIGVsZW1lbnRcbiAqIEByZXR1cm5zXG4gKi9cbmV4cG9ydCBjb25zdCBjcmVhdGVFbGVtZW50ID0gKHRhZywgb3B0aW9ucywgc3R5bGUgPSB7fSkgPT4ge1xuICBjb25zdCBlbGVtZW50ID0gT2JqZWN0LmFzc2lnbihkb2N1bWVudC5jcmVhdGVFbGVtZW50KHRhZyksIG9wdGlvbnMpO1xuICBPYmplY3QuYXNzaWduKGVsZW1lbnQuc3R5bGUsIHN0eWxlKTtcblxuICByZXR1cm4gZWxlbWVudDtcbn07XG4vKipcbiAqIENvbXB1dGUgdGhlIG51bWJlciBvZiBsaW5lcyBpbiBhbiBlbGVtZW50LlxuICogQHBhcmFtIHtIVE1MRWxlbWVudH0gZWxlbWVudCBUaGUgZWxlbWVudCB0byBjb21wdXRlIGxpbmVzIGZvci5cbiAqIEByZXR1cm5zIHtudW1iZXJ9IFRoZSBudW1iZXIgb2YgbGluZXMgaW4gdGhlIGVsZW1lbnQuXG4gKi9cbmV4cG9ydCBjb25zdCBjb21wdXRlTGluZUNvdW50ID0gKGVsZW1lbnQpID0+IHtcbiAgaWYgKCFlbGVtZW50KSB7XG4gICAgcmV0dXJuIDA7XG4gIH1cbiAgY29uc3Qgc3R5bGUgPSBnZXRDb21wdXRlZFN0eWxlKGVsZW1lbnQpO1xuICBsZXQgbGluZUhlaWdodCA9IHBhcnNlRmxvYXQoc3R5bGUubGluZUhlaWdodCk7XG5cbiAgaWYgKGlzTmFOKGxpbmVIZWlnaHQpKSB7XG4gICAgY29uc3QgZm9udFNpemUgPSBwYXJzZUZsb2F0KHN0eWxlLmZvbnRTaXplKTtcbiAgICBsaW5lSGVpZ2h0ID0gZm9udFNpemUgKiBERUZBVUxUX0xJTkVfSEVJR0hUO1xuICB9XG5cbiAgY29uc3QgZWxlbWVudEhlaWdodCA9IGVsZW1lbnQuZ2V0Qm91bmRpbmdDbGllbnRSZWN0KCkuaGVpZ2h0O1xuICBjb25zdCBudW1iZXJPZkxpbmVzRXhhY3QgPSBlbGVtZW50SGVpZ2h0IC8gbGluZUhlaWdodDtcblxuICAvLyBFbGVtZW50IGhlaWdodCBtaWdodCBiZSBzbGlnaHRseSBsYXJnZXIgb25seSwgdGhlbiBhc3N1bWluZyBvbmUgbW9yZSBsaW5lIGlzIG5vdCBjb3JyZWN0LlxuICBjb25zdCBmbG9hdGluZ1ZhbHVlID0gTWF0aC5hYnMoTWF0aC5yb3VuZChudW1iZXJPZkxpbmVzRXhhY3QpIC0gbnVtYmVyT2ZMaW5lc0V4YWN0KTtcbiAgY29uc3QgaXNDbG9zZVRvSW50ZWdlciA9IGZsb2F0aW5nVmFsdWUgPCBDTE9TRV9UT19JTlRFR0VSX0VQU0lMT047XG5cbiAgcmV0dXJuIChpc0Nsb3NlVG9JbnRlZ2VyKSA/IE1hdGgucm91bmQobnVtYmVyT2ZMaW5lc0V4YWN0KSA6IE1hdGguY2VpbChudW1iZXJPZkxpbmVzRXhhY3QpO1xufTtcblxuLyoqXG4gKiBDb21wdXRlIHRoZSB3aWR0aCByYXRpbyBiZXR3ZWVuIHR3byBlbGVtZW50cy5cbiAqIEBwYXJhbSB7SFRNTEVsZW1lbnR9IGVsZW1lbnRBIFRoZSBmaXJzdCBlbGVtZW50LlxuICogQHBhcmFtIHtIVE1MRWxlbWVudH0gZWxlbWVudEIgVGhlIHNlY29uZCBlbGVtZW50LlxuICogQHJldHVybnMge251bWJlcn0gVGhlIHdpZHRoIHJhdGlvIChlbGVtZW50QSAvIGVsZW1lbnRCKS5cbiAqL1xuZXhwb3J0IGNvbnN0IGNvbXB1dGVXaWR0aFJhdGlvID0gKGVsZW1lbnRBLCBlbGVtZW50QikgPT4ge1xuICBpZiAoIWVsZW1lbnRBIHx8ICFlbGVtZW50Qikge1xuICAgIHJldHVybiAwO1xuICB9XG5cbiAgY29uc3Qgd2lkdGhBID0gZWxlbWVudEEub2Zmc2V0V2lkdGg7XG4gIGNvbnN0IHdpZHRoQiA9IGVsZW1lbnRCLmNsaWVudFdpZHRoO1xuXG4gIGlmICghd2lkdGhBIHx8ICF3aWR0aEIpIHtcbiAgICByZXR1cm4gMDtcbiAgfVxuXG4gIHJldHVybiB3aWR0aEEgLyB3aWR0aEI7XG59O1xuXG4vKipcbiAqIERlYm91bmNlIGEgZnVuY3Rpb24gY2FsbC5cbiAqIEBwYXJhbSB7ZnVuY3Rpb259IGNhbGxiYWNrIEZ1bmN0aW9uIHRvIGRlYm91bmNlLlxuICogQHBhcmFtIHtudW1iZXJ9IGRlbGF5TXMgRGVib3VuY2luZyBkZWxheS5cbiAqIEByZXR1cm5zIHtmdW5jdGlvbn0gRGVib3VuY2VkIGZ1bmN0aW9uLlxuICovXG5leHBvcnQgY29uc3QgZGVib3VuY2UgPSAoY2FsbGJhY2ssIGRlbGF5TXMgPSBERUJPVU5DRV9ERUxBWV9NUykgPT4ge1xuICBsZXQgdGltZW91dElkO1xuICByZXR1cm4gKC4uLmFyZ3MpID0+IHtcbiAgICBjbGVhclRpbWVvdXQodGltZW91dElkKTtcbiAgICB0aW1lb3V0SWQgPSBzZXRUaW1lb3V0KCgpID0+IGNhbGxiYWNrKC4uLmFyZ3MpLCBkZWxheU1zKTtcbiAgfTtcbn07XG4iLCJpbXBvcnQgJy4uL3N0eWxlcy9oNXAtYnV0dG9uLmNzcyc7XG5pbXBvcnQgKiBhcyBVdGlscyBmcm9tICcuLi91dGlscy5qcyc7XG5cbi8qKiBAY29uc3RhbnQge251bWJlcn0gTUFYX0xBQkVMX0xJTkVfQ09VTlQgTWF4aW11bSBudW1iZXIgb2YgbGluZXMgZm9yIGxhYmVsIGJlZm9yZSBoaWRpbmcgaXQgKi9cbmNvbnN0IE1BWF9MQUJFTF9MSU5FX0NPVU5UID0gMTtcblxuLyoqXG4gKiBAY29uc3RhbnQge251bWJlcn0gTUFYX0xBQkVMX1dJRFRIX1JBVElPXG4gKiBNYXhpbXVtIHdpZHRoIHJhdGlvIGJldHdlZW4gbGFiZWwgYW5kIGJ1dHRvbiBiZWZvcmUgaGlkaW5nIGxhYmVsICovXG5jb25zdCBNQVhfTEFCRUxfV0lEVEhfUkFUSU8gPSAwLjg1O1xuXG4vKipcbiAqIEB0eXBlZGVmIHsncHJpbWFyeScgfCAnc2Vjb25kYXJ5JyB8ICduYXYnfSBCdXR0b25TdHlsZVR5cGVcbiAqL1xuXG4vKipcbiAqIEB0eXBlZGVmIHtcbiAqICAgJ2NoZWNrJyB8XG4gKiAgICdyZXRyeScgfFxuICogICAnZG9uZScgfFxuICogICAnc2hvdy1yZXN1bHRzJyB8XG4gKiAgICdib29rJyB8XG4gKiAgICdmbGlwJyB8XG4gKiAgICduZXh0JyB8XG4gKiAgICdwcmV2aW91cycgfFxuICogICAnc2hvdy1zb2x1dGlvbnMnXG4gKiB9IEJ1dHRvbkljb25cbiAqL1xuXG4vKipcbiAqIEB0eXBlZGVmIEJ1dHRvblBhcmFtc1xuICogQHR5cGUge29iamVjdH1cbiAqIEBwcm9wZXJ0eSB7c3RyaW5nfSBbbGFiZWxdIFRoZSBidXR0b24gdGV4dFxuICogQHByb3BlcnR5IHtzdHJpbmd9IFthcmlhTGFiZWxdIFRoZSBzY3JlZW5yZWFkZXIgZnJpZW5kbHkgdGV4dC4gRGVmYXVsdCBpcyBsYWJlbFxuICogQHByb3BlcnR5IHtzdHJpbmd9IFt0b29sdGlwXSBUaGUgdG9vbHRpcCB0byBzaG93IG9uIGhvdmVyL2ZvY3VzLiBEZWZhdWx0IGlzIGxhYmVsIGlmIGljb24gZW5hYmxlZFxuICogICAgTmVlZGVkIHNpbmNlIGljb24gb25seSBidXR0b24gb24gc21hbGwgc2NyZWVuc1xuICogQHByb3BlcnR5IHtCdXR0b25TdHlsZVR5cGV9IFtzdHlsZVR5cGVdIFdoaWNoICh2aXN1YWwpIHR5cGUgb2YgYnV0dG9uIGl0IGlzXG4gKiBAcHJvcGVydHkge0J1dHRvbkljb259IFtpY29uXSBXaGljaCBpY29uIHRvIHNob3cgb24gdGhlIGJ1dHRvblxuICogQHByb3BlcnR5IHtzdHJpbmdbXX0gW2NsYXNzZXNdIEFkZGl0aW9uYWwgY2xhc3NlcyB0byBhZGQgdG8gdGhlIGJ1dHRvblxuICogQHByb3BlcnR5IHtGdW5jdGlvbn0gW29uQ2xpY2tdIFRoZSBmdW5jdGlvbiB0byBwZXJmb3JtIG9uY2UgdGhlIGJ1dHRvbiBpcyBjbGlja2VkXG4gKiBAcHJvcGVydHkge3N0cmluZ30gW2J1dHRvblR5cGVdIFdoaWNoIGh0bWwgdHlwZSB0aGUgYnV0dG9uIHNob3VsZCBiZS4gRGVmYXVsdCBpcyBidXR0b25cbiAqIEBwcm9wZXJ0eSB7Ym9vbGVhbn0gW2Rpc2FibGVkXSBXaGV0aGVyIHRoZSBidXR0b24gc2hvdWxkIGJlIGVuYWJsZWQvZGlzYWJsZWQuIERlZmF1bHQgaXMgZW5hYmxlZFxuICovXG5cbi8qKlxuICogQ3JlYXRlIGEgdGhlbWVkLCByZXNwb25zaXZlIGJ1dHRvblxuICogQHBhcmFtIHtCdXR0b25QYXJhbXN9IHBhcmFtcyBBIHNldCBvZiBwYXJhbWV0ZXJzIHRvIGNvbmZpZ3VyZSB0aGUgQnV0dG9uIGNvbXBvbmVudFxuICogQHJldHVybnMge0hUTUxFbGVtZW50fSBUaGUgYnV0dG9uIGVsZW1lbnRcbiAqL1xuZnVuY3Rpb24gQnV0dG9uKHBhcmFtcykge1xuICBjb25zdCBiYXNlQ2xhc3MgPSAnaDVwLXRoZW1lLWJ1dHRvbic7XG4gIGxldCBidXR0b25TdHlsZVR5cGUgPSAnaDVwLXRoZW1lLXByaW1hcnktY3RhJztcblxuICBpZiAocGFyYW1zLnN0eWxlVHlwZSA9PT0gJ3NlY29uZGFyeScpIHtcbiAgICBidXR0b25TdHlsZVR5cGUgPSAnaDVwLXRoZW1lLXNlY29uZGFyeS1jdGEnO1xuICB9XG4gIGVsc2UgaWYgKHBhcmFtcy5zdHlsZVR5cGUgPT09ICduYXYnKSB7XG4gICAgYnV0dG9uU3R5bGVUeXBlID0gJ2g1cC10aGVtZS1uYXYtYnV0dG9uJztcbiAgfVxuXG4gIGJ1dHRvblN0eWxlVHlwZSA9IGAke2Jhc2VDbGFzc30gJHtidXR0b25TdHlsZVR5cGV9YDtcblxuICBsZXQgdG9vbHRpcDtcbiAgaWYgKHBhcmFtcy5pY29uKSB7XG4gICAgYnV0dG9uU3R5bGVUeXBlICs9IGAgaDVwLXRoZW1lLSR7cGFyYW1zLmljb259YDtcbiAgICB0b29sdGlwID0gcGFyYW1zLnRvb2x0aXAgPz8gcGFyYW1zLmxhYmVsO1xuICB9XG5cbiAgY29uc3QgYnV0dG9uID0gVXRpbHMuY3JlYXRlRWxlbWVudCgnYnV0dG9uJywge1xuICAgIGlubmVySFRNTDogcGFyYW1zLmxhYmVsID8gYDxzcGFuIGNsYXNzPVwiaDVwLXRoZW1lLWxhYmVsXCI+JHtwYXJhbXMubGFiZWx9PC9zcGFuPmAgOiAnJyxcbiAgICBhcmlhTGFiZWw6IFV0aWxzLnBhcnNlU3RyaW5nKHBhcmFtcy5hcmlhTGFiZWwgPz8gcGFyYW1zLmxhYmVsKSxcbiAgICBjbGFzc0xpc3Q6IHBhcmFtcy5jbGFzc2VzID8gYCR7YnV0dG9uU3R5bGVUeXBlfSAke3BhcmFtcy5jbGFzc2VzfWAgOiBidXR0b25TdHlsZVR5cGUsXG4gICAgb25jbGljazogcGFyYW1zLm9uQ2xpY2ssXG4gICAgdHlwZTogcGFyYW1zLmJ1dHRvblR5cGUgPz8gJ2J1dHRvbicsXG4gICAgZGlzYWJsZWQ6IHBhcmFtcy5kaXNhYmxlZCA/PyBmYWxzZSxcbiAgfSk7XG5cbiAgaWYgKHRvb2x0aXApIHtcbiAgICBINVAuVG9vbHRpcChidXR0b24sIHsgdGV4dDogdG9vbHRpcCwgcG9zaXRpb246IHBhcmFtcy50b29sdGlwUG9zaXRpb24gPz8gJ3RvcCcgfSk7XG4gIH1cblxuICBpZiAocGFyYW1zLmljb24pIHtcbiAgICBJY29uT25seU9ic2VydmVyLm9ic2VydmUoYnV0dG9uKTtcbiAgfVxuXG4gIHJldHVybiBidXR0b247XG59XG5cbmNvbnN0IEljb25Pbmx5T2JzZXJ2ZXIgPSBuZXcgUmVzaXplT2JzZXJ2ZXIoVXRpbHMuZGVib3VuY2UoKGVudHJpZXMpID0+IHtcbiAgZm9yIChjb25zdCBlbnRyeSBvZiBlbnRyaWVzKSB7XG4gICAgY29uc3QgYnV0dG9uID0gZW50cnkudGFyZ2V0O1xuICAgIGlmICghYnV0dG9uLmlzQ29ubmVjdGVkIHx8IGJ1dHRvbi5tYXRjaGVzKCc6aG92ZXInKSkge1xuICAgICAgY29udGludWU7XG4gICAgfVxuXG4gICAgY29uc3QgbGFiZWwgPSBidXR0b24ucXVlcnlTZWxlY3RvcignLmg1cC10aGVtZS1sYWJlbCcpO1xuICAgIGNvbnN0IGxpbmVDb3VudCA9IFV0aWxzLmNvbXB1dGVMaW5lQ291bnQobGFiZWwpO1xuICAgIGlmICghbGluZUNvdW50KSB7XG4gICAgICBjb250aW51ZTtcbiAgICB9XG5cbiAgICBjb25zdCByYXRpbyA9IFV0aWxzLmNvbXB1dGVXaWR0aFJhdGlvKGxhYmVsLCBidXR0b24pO1xuICAgIGNvbnN0IHNob3VsZEhpZGUgPSBsaW5lQ291bnQgPiBNQVhfTEFCRUxfTElORV9DT1VOVCB8fCByYXRpbyA+IE1BWF9MQUJFTF9XSURUSF9SQVRJTztcblxuICAgIC8vIEZvciB2aXN1YWwgY29uc2lzdGVuY3ksIGxhYmVsIG9mIHJlbGF0ZWQgYnV0dG9ucyBzaG91bGQgYmUgaGlkZGVuIGFzIHdlbGwgaWYgb25lIGlzIGhpZGRlblxuICAgIGNvbnN0IHBhcmVudCA9IGJ1dHRvbi5wYXJlbnRFbGVtZW50O1xuICAgIGZvciAoY29uc3QgY2hpbGQgb2YgcGFyZW50LmNoaWxkcmVuKSB7XG4gICAgICBpZiAoIShjaGlsZCBpbnN0YW5jZW9mIEhUTUxCdXR0b25FbGVtZW50KSB8fCAhY2hpbGQuaXNDb25uZWN0ZWQpIHtcbiAgICAgICAgY29udGludWU7XG4gICAgICB9XG4gICAgICBjaGlsZC5jbGFzc0xpc3QudG9nZ2xlKCdpY29uLW9ubHknLCBzaG91bGRIaWRlKTtcbiAgICB9XG4gIH1cbn0pKTtcblxuZXhwb3J0IGRlZmF1bHQgQnV0dG9uO1xuIiwiaW1wb3J0ICcuLi9zdHlsZXMvaDVwLWNvdmVyLXBhZ2UuY3NzJztcbmltcG9ydCB7IGNyZWF0ZUVsZW1lbnQgfSBmcm9tICcuLi91dGlscy5qcyc7XG5pbXBvcnQgQnV0dG9uIGZyb20gJy4vaDVwLWJ1dHRvbi5qcyc7XG5cbi8qKlxuICogQHR5cGVkZWYge1xuICogICAnY2hlY2snIHxcbiAqICAgJ3JldHJ5JyB8XG4gKiAgICdkb25lJyB8XG4gKiAgICdzaG93LXJlc3VsdHMnIHxcbiAqICAgJ2Jvb2snIHxcbiAqICAgJ2ZsaXAnIHxcbiAqICAgJ25leHQnIHxcbiAqICAgJ3ByZXZpb3VzJ1xuICogfSBDb3ZlclBhZ2VJY29uXG4gKi9cblxuLyoqXG4gKiBAdHlwZWRlZiBDb3ZlclBhZ2VQYXJhbXNcbiAqIEB0eXBlIHtvYmplY3R9XG4gKiBAcHJvcGVydHkge3N0cmluZ30gdGl0bGUgVGhlIHRpdGxlIGZvciB0aGUgY292ZXIgcGFnZVxuICogQHByb3BlcnR5IHtbc3RyaW5nXX0gZGVzY3JpcHRpb24gVGhlIGRlc2NyaXB0aW9uIG9yIHN1Yi10aXRsZSBvZiB0aGUgY29udGVudFxuICogQHByb3BlcnR5IHtbc3RyaW5nXX0gaW1nIFRoZSB1cmwgdG8gdGhlIGltYWdlXG4gKiBAcHJvcGVydHkge1tzdHJpbmddfSBpbWdBbHQgVGhlIGFsdCB0ZXh0IGZvciB0aGUgaW1hZ2VcbiAqIEBwcm9wZXJ0eSB7W2Jvb2xlYW5dfSB1c2VNZWRpYUNvbnRhaW5lciBBZGQgYSBjb250YWluZXIgaW5zdGVhZCBvZiBhbiBpbWdcbiAqICAgIHNvIHRoZSBjb25zdW1lciBjYW4gYXR0YWNoIGl0IHRoZW1zZWx2ZXNcbiAqIEBwcm9wZXJ0eSB7c3RyaW5nfSBidXR0b25MYWJlbCBUaGUgbGFiZWwgb2YgdGhlIGJ1dHRvblxuICogQHByb3BlcnR5IHtmdW5jdGlvbn0gYnV0dG9uT25DbGljayBUaGUgZnVuY3Rpb24gdG8gdHJpZ2dlciB3aGVuIGNsaWNraW5nIHRoZSBidXR0b25cbiAqIEBwcm9wZXJ0eSB7W0NvdmVyUGFnZUljb25dfSBpY29uIFRoZSBuYW1lIG9mIHRoZSBpY29uIHRvIHVzZSBmb3IgdGhlIGJ1dHRvbiBhbmQgYWJvdmUgdGhlIHRpdGxlXG4gKi9cblxuLyoqXG4gKiBDcmVhdGUgYSB0aGVtZWQsIHJlc3BvbnNpdmUgY292ZXIgcGFnZVxuICogQHBhcmFtIHtDb3ZlclBhZ2VQYXJhbXN9IHBhcmFtcyBBIHNldCBvZiBwYXJhbWV0ZXJzIHRvIGNvbmZpZ3VyZSB0aGUgQ292ZXJQYWdlIGNvbXBvbmVudFxuICogQHJldHVybnMge0hUTUxFbGVtZW50fSBUaGUgY292ZXIgcGFnZSBlbGVtZW50XG4gKi9cbmZ1bmN0aW9uIENvdmVyUGFnZShwYXJhbXMpIHtcbiAgbGV0IGNvdmVyUGFnZUNsYXNzZXMgPSAnaDVwLXRoZW1lLWNvdmVyLXBhZ2UnO1xuXG4gIGlmIChwYXJhbXMudXNlTWVkaWFDb250YWluZXIgfHwgcGFyYW1zLmltZykge1xuICAgIGNvdmVyUGFnZUNsYXNzZXMgKz0gJyBoNXAtdGhlbWUtY292ZXItcGFnZS13aXRoLWltYWdlJztcbiAgfVxuXG4gIGNvbnN0IGNvdmVyUGFnZSA9IGNyZWF0ZUVsZW1lbnQoJ2RpdicsIHtcbiAgICBjbGFzc0xpc3Q6IGNvdmVyUGFnZUNsYXNzZXMsXG4gIH0pO1xuXG4gIGNvdmVyUGFnZS5hcHBlbmRDaGlsZChjcmVhdGVFbGVtZW50KCdkaXYnLCB7XG4gICAgY2xhc3NMaXN0OiAnaDVwLXRoZW1lLXBhdHRlcm4tY29udGFpbmVyJyxcbiAgICBpbm5lckhUTUw6ICc8ZGl2IGNsYXNzPVwiaDVwLXRoZW1lLXBhdHRlcm5cIj48L2Rpdj4nLFxuICB9KSk7XG5cbiAgaWYgKHBhcmFtcy51c2VNZWRpYUNvbnRhaW5lcikge1xuICAgIGNvdmVyUGFnZS5hcHBlbmRDaGlsZChjcmVhdGVFbGVtZW50KCdkaXYnLCB7XG4gICAgICBjbGFzc0xpc3Q6ICdoNXAtdGhlbWUtY292ZXItaW1nJyxcbiAgICB9KSk7XG4gIH1cbiAgZWxzZSBpZiAocGFyYW1zLmltZykge1xuICAgIGNvdmVyUGFnZS5hcHBlbmRDaGlsZChjcmVhdGVFbGVtZW50KCdpbWcnLCB7XG4gICAgICBzcmM6IHBhcmFtcy5pbWcsXG4gICAgICBhbHQ6IHBhcmFtcy5pbWdBbHQgPz8gJycsXG4gICAgICBjbGFzc0xpc3Q6ICdoNXAtdGhlbWUtY292ZXItaW1nJyxcbiAgICB9KSk7XG4gIH1cblxuICBjb25zdCBkZXRhaWxDb250YWluZXIgPSBjcmVhdGVFbGVtZW50KCdkaXYnLCB7IGNsYXNzTGlzdDogJ2g1cC10aGVtZS1jb3Zlci1kZXRhaWxzJyB9KTtcblxuICBpZiAocGFyYW1zLmljb24pIHtcbiAgICBkZXRhaWxDb250YWluZXIuYXBwZW5kQ2hpbGQoY3JlYXRlRWxlbWVudCgnc3BhbicsIHtcbiAgICAgIGNsYXNzTGlzdDogYGg1cC10aGVtZS1jb3Zlci1pY29uIGg1cC10aGVtZS0ke3BhcmFtcy5pY29ufWAsXG4gICAgICBhcmlhSGlkZGVuOiB0cnVlLFxuICAgIH0pKTtcbiAgfVxuXG4gIGRldGFpbENvbnRhaW5lci5hcHBlbmRDaGlsZChjcmVhdGVFbGVtZW50KCdoMicsIHtcbiAgICB0ZXh0Q29udGVudDogcGFyYW1zLnRpdGxlLFxuICB9KSk7XG5cbiAgaWYgKHBhcmFtcy5kZXNjcmlwdGlvbikge1xuICAgIGRldGFpbENvbnRhaW5lci5hcHBlbmRDaGlsZChjcmVhdGVFbGVtZW50KCdwJywge1xuICAgICAgY2xhc3NMaXN0OiAnaDVwLXRoZW1lLWNvdmVyLWRlc2NyaXB0aW9uJyxcbiAgICAgIGlubmVySFRNTDogcGFyYW1zLmRlc2NyaXB0aW9uLFxuICAgIH0pKTtcbiAgfVxuXG4gIGRldGFpbENvbnRhaW5lci5hcHBlbmRDaGlsZChCdXR0b24oe1xuICAgIGxhYmVsOiBwYXJhbXMuYnV0dG9uTGFiZWwsXG4gICAgaWNvbjogcGFyYW1zLmljb24sXG4gICAgb25DbGljazogcGFyYW1zLmJ1dHRvbk9uQ2xpY2ssXG4gIH0pKTtcblxuICBjb3ZlclBhZ2UuYXBwZW5kQ2hpbGQoZGV0YWlsQ29udGFpbmVyKTtcblxuICByZXR1cm4gY292ZXJQYWdlO1xufVxuXG5leHBvcnQgZGVmYXVsdCBDb3ZlclBhZ2U7XG4iLCJpbXBvcnQgJy4uL3N0eWxlcy9oNXAtZHJhZ2dhYmxlLmNzcyc7XG5pbXBvcnQgeyBjcmVhdGVFbGVtZW50IH0gZnJvbSAnLi4vdXRpbHMuanMnO1xuXG4vKipcbiAqIEB0eXBlZGVmIERyYWdnYWJsZVBhcmFtc1xuICogQHR5cGUge29iamVjdH1cbiAqIEBwcm9wZXJ0eSB7c3RyaW5nfSBsYWJlbCBBIGxhYmVsIGZvciB0aGUgZHJhZ2dhYmxlIGVsZW1lbnRcbiAqIEBwcm9wZXJ0eSB7SFRNTEVsZW1lbnR9IFtkb21dXG4gKiAgICBBIERPTSBlbGVtZW50IHRvIHVzZSBhcyB0aGUgZHJhZ2dhYmxlIGVsZW1lbnQgTGFiZWwgd2lsbCBiZSB1c2VkIGFzIGZhbGxiYWNrXG4gKiBAcHJvcGVydHkge251bWJlcn0gW3RhYkluZGV4XSBUYWJpbmRleCB0byB1c2Ugb24gdGhlIGRyYWdnYWJsZSBlbGVtZW50IChkZWZhdWx0IDApXG4gKiBAcHJvcGVydHkge2Jvb2xlYW59IFthcmlhR3JhYmJlZF0gSW5pdGlhbGl6ZSB0aGUgZ3JhYmJlZCBzdGF0ZSBvbiB0aGUgZHJhZ2dhYmxlIChkZWZhdWx0IGZhbHNlKVxuICogQHByb3BlcnR5IHtib29sZWFufSBbaGFzSGFuZGxlXSBBIGJvb2xlYW4gZGV0ZXJtaW5pbmcgaWYgdGhlIGRyYWdnYWJsZSBoYXMgdmlzdWFsIGhhbmRsZXMgb3Igbm90XG4gKiBAcHJvcGVydHkge2Z1bmN0aW9ufSBoYW5kbGVSZXZlcnQgQSBjYWxsYmFjayBmdW5jdGlvbiB0byBoYW5kbGUgcmV2ZXJ0XG4gKiBAcHJvcGVydHkge2Z1bmN0aW9ufSBoYW5kbGVEcmFnRXZlbnQgQSBjYWxsYmFjayBmdW5jdGlvbiBmb3IgdGhlIGRyYWcgZXZlbnRcbiAqIEBwcm9wZXJ0eSB7ZnVuY3Rpb259IGhhbmRsZURyYWdTdGFydEV2ZW50IEEgY2FsbGJhY2sgZnVuY3Rpb24gZm9yIHRoZSBkcmFnc3RhcnQgZXZlbnRcbiAqIEBwcm9wZXJ0eSB7ZnVuY3Rpb259IGhhbmRsZURyYWdTdG9wRXZlbnQgQSBjYWxsYmFjayBmdW5jdGlvbiBmb3IgdGhlIGRyYWdlbmQgZXZlbnRcbiAqL1xuXG4vKipcbiAqIENyZWF0ZSBhIHRoZW1lZCwgRHJhZ2dhYmxlIGVsZW1lbnRcbiAqIEBwYXJhbSB7RHJhZ2dhYmxlUGFyYW1zfSBwYXJhbXMgQSBzZXQgb2YgcGFyYW1ldGVycyB0byBjb25maWd1cmUgdGhlIERyYWdnYWJsZSBjb21wb25lbnRcbiAqIEByZXR1cm5zIHtIVE1MRWxlbWVudH0gVGhlIERyYWdnYWJsZSBlbGVtZW50XG4gKi9cbmZ1bmN0aW9uIERyYWdnYWJsZShwYXJhbXMpIHtcbiAgbGV0IGNsYXNzZXMgPSAnaDVwLWRyYWdnYWJsZSc7XG5cbiAgaWYgKHBhcmFtcy5oYXNIYW5kbGUpIHtcbiAgICBjbGFzc2VzICs9ICcgaDVwLWRyYWdnYWJsZS0taGFzLWhhbmRsZSc7XG4gIH1cblxuICBpZiAocGFyYW1zLnN0YXR1c0NoYW5nZXNCYWNrZ3JvdW5kKSB7XG4gICAgY2xhc3NlcyArPSAnIGg1cC1kcmFnZ2FibGUtLWJhY2tncm91bmQtc3RhdHVzJztcbiAgfVxuXG4gIGlmIChwYXJhbXMucG9pbnRzQW5kU3RhdHVzKSB7XG4gICAgY2xhc3NlcyArPSAnIGg1cC1kcmFnZ2FibGUtLXBvaW50cy1hbmQtc3RhdHVzJztcbiAgfVxuXG4gIGNvbnN0IHNldENvbnRlbnQgPSAoeyBkb20sIGxhYmVsIH0pID0+IHtcbiAgICBkcmFnZ2FibGUuaW5uZXJIVE1MID0gJyc7XG4gICAgaWYgKGRvbSkge1xuICAgICAgZHJhZ2dhYmxlLmFwcGVuZChkb20pO1xuICAgIH1cbiAgICBlbHNlIHtcbiAgICAgIGRyYWdnYWJsZS5pbm5lckhUTUwgPSBgPHNwYW4+JHtsYWJlbH08L3NwYW4+PHNwYW4gY2xhc3M9XCJoNXAtaGlkZGVuLXJlYWRcIj48L3NwYW4+YDtcbiAgICB9XG4gIH07XG5cbiAgY29uc3QgZHJhZ2dhYmxlID0gY3JlYXRlRWxlbWVudCgnZGl2Jywge1xuICAgIGNsYXNzTGlzdDogY2xhc3NlcyxcbiAgICByb2xlOiAnYnV0dG9uJyxcbiAgICB0YWJJbmRleDogcGFyYW1zLnRhYkluZGV4ID8/IDAsXG4gIH0pO1xuXG4gIHNldENvbnRlbnQoeyBkb206IHBhcmFtcy5kb20sIGxhYmVsOiBwYXJhbXMubGFiZWwgfSk7XG5cbiAgLy8gSGF2ZSB0byBzZXQgaXQgbGlrZSB0aGlzLCBiZWNhdXNlIGl0IGNhbm5vdCBiZSBzZXQgd2l0aCBjcmVhdGVFbGVtZW50XG4gIGRyYWdnYWJsZS5zZXRBdHRyaWJ1dGUoJ2FyaWEtZ3JhYmJlZCcsIHBhcmFtcy5hcmlhR3JhYmJlZCA/PyBmYWxzZSk7XG5cbiAgLy8gVXNlIGpRdWVyeSBkcmFnZ2FibGUgKGZvciBub3cpXG4gIEg1UC5qUXVlcnkoZHJhZ2dhYmxlKS5kcmFnZ2FibGUoe1xuICAgIHJldmVydDogcGFyYW1zLmhhbmRsZVJldmVydCxcbiAgICBkcmFnOiBwYXJhbXMuaGFuZGxlRHJhZ0V2ZW50LFxuICAgIHN0YXJ0OiBwYXJhbXMuaGFuZGxlRHJhZ1N0YXJ0RXZlbnQsXG4gICAgc3RvcDogcGFyYW1zLmhhbmRsZURyYWdTdG9wRXZlbnQsXG4gICAgY29udGFpbm1lbnQ6IHBhcmFtcy5jb250YWlubWVudCxcbiAgfSk7XG5cbiAgLyoqXG4gICAqIFNldCBvcGFjaXR5IG9mIGVsZW1lbnQgY29udGVudFxuICAgKiBAcGFyYW0ge251bWJlcn0gdmFsdWUgT3BhY2l0eSB2YWx1ZSBiZXR3ZWVuIDAgYW5kIDEwMFxuICAgKi9cbiAgY29uc3Qgc2V0Q29udGVudE9wYWNpdHkgPSAodmFsdWUpID0+IHtcbiAgICBjb25zdCBzYW5pdGl6ZWRWYWx1ZSA9IE1hdGgubWF4KDAsIE1hdGgubWluKE51bWJlcih2YWx1ZSkgPz8gMTAwLCAxMDApKSAvIDEwMDtcbiAgICBkcmFnZ2FibGUuc3R5bGUuc2V0UHJvcGVydHkoJy0tY29udGVudC1vcGFjaXR5Jywgc2FuaXRpemVkVmFsdWUpO1xuICB9O1xuXG4gIGNvbnN0IHNldE9wYWNpdHkgPSAodmFsdWUpID0+IHtcbiAgICBjb25zdCBzYW5pdGl6ZWRWYWx1ZSA9IE1hdGgubWF4KDAsIE1hdGgubWluKE51bWJlcih2YWx1ZSkgPz8gMTAwLCAxMDApKSAvIDEwMDtcbiAgICBkcmFnZ2FibGUuc3R5bGUuc2V0UHJvcGVydHkoJy0tb3BhY2l0eScsIHNhbml0aXplZFZhbHVlKTtcbiAgfTtcblxuICBjb25zdCBzZXREcmFnSGFuZGxlVmlzaWJpbGl0eSA9ICh2YWx1ZSkgPT4ge1xuICAgIGRyYWdnYWJsZS5jbGFzc0xpc3QudG9nZ2xlKCdoNXAtZHJhZ2dhYmxlLS1oYXMtaGFuZGxlJywgdmFsdWUpO1xuICB9O1xuXG4gIGNvbnN0IGdldEJvcmRlcldpZHRoID0gKCkgPT4ge1xuICAgIGNvbnN0IGNvbXB1dGVkU3R5bGUgPSB3aW5kb3cuZ2V0Q29tcHV0ZWRTdHlsZShkcmFnZ2FibGUpO1xuICAgIHJldHVybiBjb21wdXRlZFN0eWxlLmdldFByb3BlcnR5VmFsdWUoJy0tYm9yZGVyLXdpZHRoJyk7XG4gIH07XG5cbiAgZHJhZ2dhYmxlLnNldENvbnRlbnRPcGFjaXR5ID0gc2V0Q29udGVudE9wYWNpdHk7XG4gIGRyYWdnYWJsZS5zZXRPcGFjaXR5ID0gc2V0T3BhY2l0eTtcbiAgZHJhZ2dhYmxlLmdldEJvcmRlcldpZHRoID0gZ2V0Qm9yZGVyV2lkdGg7XG4gIGRyYWdnYWJsZS5zZXRDb250ZW50ID0gc2V0Q29udGVudDtcbiAgZHJhZ2dhYmxlLnNldERyYWdIYW5kbGVWaXNpYmlsaXR5ID0gc2V0RHJhZ0hhbmRsZVZpc2liaWxpdHk7XG5cbiAgcmV0dXJuIGRyYWdnYWJsZTtcbn1cblxuZXhwb3J0IGRlZmF1bHQgRHJhZ2dhYmxlO1xuIiwiaW1wb3J0ICcuLi9zdHlsZXMvaDVwLWRyb3B6b25lLmNzcyc7XG5pbXBvcnQgeyBjcmVhdGVFbGVtZW50IH0gZnJvbSAnLi4vdXRpbHMuanMnO1xuXG4vKipcbiAqIEB0eXBlZGVmIHsnZml0JyB8ICdpbnRlcnNlY3QnIHwgJ3BvaW50ZXInIHwgJ3RvdWNoJ30gRHJvcHpvbmVUb2xlcmFuY2VcbiAqIEB0eXBlZGVmIHsnaW5saW5lJyB8ICdhcmVhJ30gRHJvcHpvbmVWYXJpYW50XG4gKi9cblxuLyoqXG4gKiBAdHlwZWRlZiBEcm9wem9uZVBhcmFtc1xuICogQHR5cGUge29iamVjdH1cbiAqIEBwcm9wZXJ0eSB7c3RyaW5nfSByb2xlIFJvbGUgZm9yIHRoZSBkcm9wem9uZVxuICogQHByb3BlcnR5IHtzdHJpbmd9IGFyaWFMYWJlbCBBIGxhYmVsIGZvciB0aGUgZHJvcHpvbmUgZWxlbWVudFxuICogQHByb3BlcnR5IHtudW1iZXJ9IFtpbmRleF1cbiAqICAgIEFuIGluZGV4IHRvIHRyYWNrIHdoaWNoIGRyb3B6b25lIHRoaXMgZWxlbWVudCBpcyBpbiBhIHNldCBEZWZhdWx0cyB0byAtMVxuICogQHByb3BlcnR5IHtib29sZWFufSBhcmlhRGlzYWJsZWQgSWYgdGhlIGRyb3B6b25lIHNob3VsZCBiZSBhcmlhIGRpc2FibGVkXG4gKiBAcHJvcGVydHkge3N0cmluZ30gW2NsYXNzZXNdIEV4dHJhIGNsYXNzZXMgdG8gYmUgYWRkZWQgdG8gdGhlIGRyb3B6b25lXG4gKiBAcHJvcGVydHkge3N0cmluZ30gW2NvbnRhaW5lckNsYXNzZXNdIEV4dHJhIGNsYXNzZXMgdG8gYmUgYWRkZWQgdG8gdGhlIGNvbnRhaW5lciBvZiB0aGUgZHJvcHpvbmVcbiAqIEBwcm9wZXJ0eSB7bnVtYmVyfSBbdGFiSW5kZXhdIFRhYmluZGV4IHRvIHVzZSBvbiB0aGUgZHJvcHpvbmUgZWxlbWVudCAoZGVmYXVsdCAtMSlcbiAqIEBwcm9wZXJ0eSB7Ym9vbGVhbn0gW2JhY2tncm91bmRPcGFjaXR5XSBUaGUgbGV2ZWwgb2Ygb3BhY2l0eSBvbiB0aGUgZHJvcHpvbmUgKDAtMTAwKVxuICogQHByb3BlcnR5IHtEcm9wem9uZVZhcmlhbnR9IFt2YXJpYW50XSBUaGUgdHlwZSBvZiBkcm9wem9uZSB0byB1c2UuIERlZmF1bHQgaXMgJ2lubGluZSdcbiAqIEBwcm9wZXJ0eSB7RHJvcHpvbmVUb2xlcmFuY2V9IHRvbGVyYW5jZVxuICogICAgU3BlY2lmaWVzIHdoaWNoIG1vZGUgdG8gdXNlIGZvciB0ZXN0aW5nIHdoZXRoZXIgZHJhZ2dhYmxlIGlzIGhvdmVyaW5nIG92ZXIgYSBkcm9wcGFibGVcbiAqIEBwcm9wZXJ0eSB7c3RyaW5nfSBbYXJlYUxhYmVsXSBBIGxhYmVsIHVzZWQgZm9yIGEgZHJvcHpvbmUgYXJlYVxuICogQHByb3BlcnR5IHtmdW5jdGlvbn0gaGFuZGxlQWNjZXB0RXZlbnQgQSBmdW5jdGlvbiBmb3IganF1ZXJ5LWRyb3BwYWJsZSBhY2NlcHQgb3B0aW9uXG4gKiBAcHJvcGVydHkge2Z1bmN0aW9ufSBoYW5kbGVEcm9wRXZlbnQgQSBjYWxsYmFjayBmdW5jdGlvbiBmb3IgdGhlIGRyb3AgZXZlbnRcbiAqIEBwcm9wZXJ0eSB7ZnVuY3Rpb259IGhhbmRsZURyb3BPdXRFdmVudCBBIGNhbGxiYWNrIGZ1bmN0aW9uIGZvciB0aGUgb3V0IGV2ZW50XG4gKiBAcHJvcGVydHkge2Z1bmN0aW9ufSBoYW5kbGVEcm9wT3ZlckV2ZW50IEEgY2FsbGJhY2sgZnVuY3Rpb24gZm9yIHRoZSBvdmVyIGV2ZW50XG4gKi9cblxuLyoqXG4gKiBDcmVhdGUgYSB0aGVtZWQsIERyb3B6b25lIGVsZW1lbnRcbiAqIEBwYXJhbSB7RHJvcHpvbmVQYXJhbXN9IHBhcmFtcyBBIHNldCBvZiBwYXJhbWV0ZXJzIHRvIGNvbmZpZ3VyZSB0aGUgRHJvcHpvbmUgY29tcG9uZW50XG4gKiBAcmV0dXJucyB7SFRNTEVsZW1lbnR9IFRoZSBkcm9wem9uZSBlbGVtZW50XG4gKi9cbmZ1bmN0aW9uIERyb3B6b25lKHBhcmFtcykge1xuICBjb25zdCBjbGFzc0xpc3QgPSBbJ2g1cC1kcm9wem9uZScsXG4gICAgcGFyYW1zLnZhcmlhbnQgPT09ICdhcmVhJyA/ICdoNXAtZHJvcHpvbmUtLWFyZWEnIDogJ2g1cC1kcm9wem9uZS0taW5saW5lJyxcbiAgXTtcblxuICBpZiAodHlwZW9mIHBhcmFtcy5jb250YWluZXJDbGFzc2VzID09PSAnc3RyaW5nJykge1xuICAgIGNsYXNzTGlzdC5wdXNoKHBhcmFtcy5jb250YWluZXJDbGFzc2VzKTtcbiAgfVxuXG4gIGlmIChwYXJhbXMuYmFja2dyb3VuZE9wYWNpdHkgPT09IDApIHtcbiAgICBjbGFzc0xpc3QucHVzaCgnaDVwLWRyb3B6b25lLS10cmFuc3BhcmVudC1iYWNrZ3JvdW5kJyk7XG4gIH1cbiAgZWxzZSBpZiAocGFyYW1zLmJhY2tncm91bmRPcGFjaXR5ID09PSAxMDApIHtcbiAgICBjbGFzc0xpc3QucHVzaCgnaDVwLWRyb3B6b25lLS1vcGFxdWUtYmFja2dyb3VuZCcpO1xuICB9XG5cbiAgY29uc3Qgb3B0aW9ucyA9IHtcbiAgICBjbGFzc0xpc3Q6IGNsYXNzTGlzdC5qb2luKCcgJyksXG4gICAgcm9sZTogcGFyYW1zLnJvbGUsXG4gICAgYXJpYURpc2FibGVkOiBwYXJhbXMuYXJpYURpc2FibGVkLFxuICB9O1xuXG4gIGNvbnN0IGRyb3B6b25lQ29udGFpbmVyID0gY3JlYXRlRWxlbWVudCgnZGl2Jywgb3B0aW9ucyk7XG5cbiAgaWYgKHBhcmFtcy52YXJpYW50ID09PSAnYXJlYScgJiYgcGFyYW1zLmFyZWFMYWJlbCkge1xuICAgIGNvbnN0IGFyZWFMYWJlbCA9IGNyZWF0ZUVsZW1lbnQoJ2RpdicsIHsgY2xhc3NMaXN0OiAnaDVwLWRyb3B6b25lX2xhYmVsJyB9KTtcbiAgICBhcmVhTGFiZWwuaW5uZXJIVE1MID0gcGFyYW1zLmFyZWFMYWJlbDtcbiAgICBkcm9wem9uZUNvbnRhaW5lci5hcHBlbmRDaGlsZChhcmVhTGFiZWwpO1xuICB9XG5cbiAgY29uc3QgJGRyb3B6b25lID0gSDVQLmpRdWVyeSgnPGRpdi8+Jywge1xuICAgICdhcmlhLWRyb3BlZmZlY3QnOiAnbm9uZScsXG4gICAgJ2FyaWEtbGFiZWwnOiBwYXJhbXMuYXJpYUxhYmVsLFxuICAgIHRhYmluZGV4OiBwYXJhbXMudGFiSW5kZXggPz8gLTEsXG4gICAgY2xhc3M6IHBhcmFtcy5jbGFzc2VzID8gcGFyYW1zLmNsYXNzZXMgOiAnJyxcbiAgfSkuYXBwZW5kVG8oZHJvcHpvbmVDb250YWluZXIpXG4gICAgLmRyb3BwYWJsZSh7XG4gICAgICBhY3RpdmVDbGFzczogJ2g1cC1kcm9wem9uZS0tYWN0aXZlJyxcbiAgICAgIHRvbGVyYW5jZTogcGFyYW1zLnRvbGVyYW5jZSxcbiAgICAgIGFjY2VwdDogcGFyYW1zLmhhbmRsZUFjY2VwdEV2ZW50LFxuICAgICAgb3ZlcjogKGV2ZW50LCB1aSkgPT4ge1xuICAgICAgICBkcm9wem9uZS5jbGFzc0xpc3QuYWRkKCdoNXAtZHJvcHpvbmUtLWhvdmVyJyk7XG4gICAgICAgIHBhcmFtcy5oYW5kbGVEcm9wT3ZlckV2ZW50Py4oZXZlbnQsIHVpKTtcbiAgICAgIH0sXG4gICAgICBvdXQ6IChldmVudCwgdWkpID0+IHtcbiAgICAgICAgZHJvcHpvbmUuY2xhc3NMaXN0LnJlbW92ZSgnaDVwLWRyb3B6b25lLS1ob3ZlcicpO1xuICAgICAgICBwYXJhbXMuaGFuZGxlRHJvcE91dEV2ZW50Py4oZXZlbnQsIHVpKTtcbiAgICAgIH0sXG4gICAgICBkcm9wOiAoZXZlbnQsIHVpKSA9PiB7XG4gICAgICAgIGRyb3B6b25lLmNsYXNzTGlzdC5yZW1vdmUoJ2g1cC1kcm9wem9uZS0taG92ZXInKTtcbiAgICAgICAgcGFyYW1zLmhhbmRsZURyb3BFdmVudD8uKGV2ZW50LCB1aSwgcGFyYW1zLmluZGV4ID8/IC0xKTtcbiAgICAgIH0sXG4gICAgfSk7XG4gIGNvbnN0IGRyb3B6b25lID0gJGRyb3B6b25lLmdldCgwKTtcblxuICByZXR1cm4gZHJvcHpvbmVDb250YWluZXI7XG59XG5cbmV4cG9ydCBkZWZhdWx0IERyb3B6b25lO1xuIiwiaW1wb3J0ICcuLi9zdHlsZXMvaDVwLXByb2dyZXNzLWJhci5jc3MnO1xuaW1wb3J0IHsgY3JlYXRlRWxlbWVudCB9IGZyb20gJy4uL3V0aWxzLmpzJztcblxuLyoqXG4gKiBAdHlwZWRlZiBQcm9ncmVzc0JhclBhcmFtc1xuICogQHR5cGUge29iamVjdH1cbiAqIEBwcm9wZXJ0eSB7bnVtYmVyfSBbaW5kZXhdIFRoZSBjdXJyZW50IHBvc2l0aW9uIGluIHRoZSBuYXZpZ2F0aW9uIChkZWZhdWx0OiAwKVxuICogQHByb3BlcnR5IHtudW1iZXJ9IFtwcm9ncmVzc0xlbmd0aF0gVGhlIG51bWJlciBvZiBcIml0ZW1zXCIgd2UgY2FuIG5hdmlnYXRlIHRocm91Z2ggKGRlZmF1bHQ6IDEpXG4gKiBAcHJvcGVydHkge251bWJlcn0gW2FyaWFWYWx1ZU1heF0gVGhlIG1heCB2YWx1ZSBvZiB0aGUgc2xpZGVyIChkZWZhdWx0OiAxMDApXG4gKiBAcHJvcGVydHkge251bWJlcn0gW2FyaWFWYWx1ZU1pbl0gVGhlIG1pbiB2YWx1ZSBvZiB0aGUgc2xpZGVyIChkZWZhdWx0OiAwKVxuICogQHByb3BlcnR5IHtudW1iZXJ9IFthcmlhVmFsdWVOb3ddIFRoZSBjdXJyZW50L2luaXRpYWwgdmFsdWUgb2YgdGhlIHNsaWRlciAoZGVmYXVsdDogMClcbiAqL1xuXG4vKipcbiAqIENyZWF0ZXMgYSBwcm9ncmVzcyBiYXIuXG4gKiBAcGFyYW0ge1Byb2dyZXNzQmFyUGFyYW1zfSBwYXJhbXMgQSBzZXQgb2YgcGFyYW1ldGVycyB0byBjb25maWd1cmUgUHJvZ3Jlc3NCYXJcbiAqIEByZXR1cm5zIHtIVE1MRWxlbWVudH0gVGhlIFByb2dyZXNzQmFyIGVsZW1lbnQuXG4gKi9cbmZ1bmN0aW9uIFByb2dyZXNzQmFyKHBhcmFtcyA9IHt9KSB7XG4gIGNvbnN0IHByb2dyZXNzTGVuZ3RoID0gcGFyYW1zLnByb2dyZXNzTGVuZ3RoID8/IDE7XG5cbiAgbGV0IGluZGV4ID0gcGFyYW1zLmluZGV4ID8/IDA7XG5cbiAgY29uc3QgcHJvZ3Jlc3NCYXIgPSBjcmVhdGVFbGVtZW50KCdkaXYnLCB7XG4gICAgY2xhc3NMaXN0OiAnaDVwLXZpc3VhbC1wcm9ncmVzcycsXG4gICAgcm9sZTogJ3Byb2dyZXNzYmFyJyxcbiAgICBhcmlhVmFsdWVNYXg6IHBhcmFtcy5hcmlhVmFsdWVNYXggPz8gMTAwLFxuICAgIGFyaWFWYWx1ZU1pbjogcGFyYW1zLmFyaWFWYWx1ZU1pbiA/PyAwLFxuICAgIGFyaWFWYWx1ZU5vdzogcGFyYW1zLmFyaWFWYWx1ZU5vdyA/PyAwLFxuICB9KTtcblxuICBjb25zdCBwcm9ncmVzc0JhcklubmVyID0gY3JlYXRlRWxlbWVudCgnZGl2Jywge1xuICAgIGNsYXNzTGlzdDogJ2g1cC12aXN1YWwtcHJvZ3Jlc3MtaW5uZXInLFxuICB9KTtcblxuICBwcm9ncmVzc0Jhci5hcHBlbmRDaGlsZChwcm9ncmVzc0JhcklubmVyKTtcblxuICBjb25zdCB1cGRhdGVQcm9ncmVzc0JhciA9IChuZXdJbmRleCkgPT4ge1xuICAgIGluZGV4ID0gbmV3SW5kZXg7XG4gICAgcHJvZ3Jlc3NCYXIuc2V0QXR0cmlidXRlKCdhcmlhLXZhbHVlbm93JywgKCgobmV3SW5kZXggKyAxKSAvIHByb2dyZXNzTGVuZ3RoKSAqIDEwMCkudG9GaXhlZCgyKSk7XG4gICAgcHJvZ3Jlc3NCYXJJbm5lci5zdHlsZS53aWR0aCA9IGAkeygobmV3SW5kZXggKyAxKSAvIHByb2dyZXNzTGVuZ3RoKSAqIDEwMH0lYDtcbiAgfTtcblxuICB1cGRhdGVQcm9ncmVzc0JhcihpbmRleCk7XG5cbiAgcHJvZ3Jlc3NCYXIudXBkYXRlUHJvZ3Jlc3NCYXIgPSB1cGRhdGVQcm9ncmVzc0JhcjtcblxuICByZXR1cm4gcHJvZ3Jlc3NCYXI7XG59XG5cbmV4cG9ydCBkZWZhdWx0IFByb2dyZXNzQmFyO1xuIiwiaW1wb3J0ICcuLi9zdHlsZXMvaDVwLXByb2dyZXNzLWRvdHMuY3NzJztcbmltcG9ydCB7IGNyZWF0ZUVsZW1lbnQgfSBmcm9tICcuLi91dGlscy5qcyc7XG4vKipcbiAqIEB0eXBlZGVmIFByb2dyZXNzRG90c1xuICogQHR5cGUge29iamVjdH1cbiAqIEBwcm9wZXJ0eSB7c3RyaW5nfSBhcmlhTGFiZWwgQSBsYWJlbCBmb3Igc2NyZWVuIHJlYWRlciB1c2VycyB3aGVuIG5hdmlnYXRpbmcgdG8gYSBkb3RcbiAqIEBwcm9wZXJ0eSB7W251bWJlcl19IHRhYkluZGV4IEluaXRpYWwgdGFiSW5kZXggZm9yIGEgZG90XG4gKi9cblxuLyoqXG4gKiBAdHlwZWRlZiBQcm9ncmVzc0RvdHNUZXh0c1xuICogQHR5cGUge29iamVjdH1cbiAqIEBwcm9wZXJ0eSB7c3RyaW5nfSBqdW1wVG9RdWVzdGlvblxuICogQHByb3BlcnR5IHtzdHJpbmd9IGFuc3dlcmVkVGV4dFxuICogQHByb3BlcnR5IHtzdHJpbmd9IHVuYW5zd2VyZWRUZXh0XG4gKiBAcHJvcGVydHkge3N0cmluZ30gY3VycmVudFF1ZXN0aW9uVGV4dFxuICovXG5cbi8qKlxuICogQHR5cGVkZWYgUHJvZ3Jlc3NEb3RzUGFyYW1zXG4gKiBAdHlwZSB7b2JqZWN0fVxuICogQHByb3BlcnR5IHtbbnVtYmVyXX0gaW5kZXggVGhlIGN1cnJlbnQgcG9zaXRpb24gaW4gdGhlIG5hdmlnYXRpb25cbiAqIEBwcm9wZXJ0eSB7UHJvZ3Jlc3NEb3RzW119IGRvdHMgQXJyYXkgb2YgZG90cyB0byBwcm9jZXNzXG4gKiBAcHJvcGVydHkge1Byb2dyZXNzRG90c1RleHRzfSB0ZXh0cyBBIGNvbGxlY3Rpb24gb2YgdHJhbnNsYXRhYmxlIHN0cmluZ3NcbiAqIEBwcm9wZXJ0eSB7W2Z1bmN0aW9uXX0gaGFuZGxlUHJvZ3Jlc3NEb3RDbGljayBBIGNhbGxiYWNrIGZ1bmN0aW9uIHdoZW4gYSBkb3QgaXMgY2xpY2tlZFxuICovXG5cbi8qKlxuICogQ3JlYXRlcyBuYXZpZ2F0aW9uYWwgZG90c1xuICogQHBhcmFtIHtQcm9ncmVzc0RvdHNQYXJhbXN9IHBhcmFtcyBBIHNldCBvZiBwYXJhbWV0ZXJzIHRvIGNvbmZpZ3VyZSBQcm9ncmVzc0RvdHNcbiAqIEByZXR1cm5zIHtIVE1MRWxlbWVudH0gVGhlIFByb2dyZXNzRG90cyBlbGVtZW50XG4gKi9cbmZ1bmN0aW9uIFByb2dyZXNzRG90cyhwYXJhbXMgPSB7fSkge1xuICBjb25zdCBwcm9ncmVzc0xlbmd0aCA9IHBhcmFtcy5kb3RzLmxlbmd0aDtcblxuICBsZXQgYWN0aXZlSW5kZXggPSBwYXJhbXMuaW5kZXggPz8gMDtcbiAgY29uc3QgcHJvZ3Jlc3NEb3RFbGVtZW50cyA9IFtdO1xuXG4gIGNvbnN0IGRvdHNDb250YWluZXIgPSBjcmVhdGVFbGVtZW50KCd1bCcsIHtcbiAgICBjbGFzc05hbWU6ICdoNXAtcHJvZ3Jlc3MtZG90cy1jb250YWluZXInLFxuICB9KTtcblxuICBjb25zdCBvblByb2dyZXNzRG90Q2xpY2sgPSAoZXZlbnQpID0+IHtcbiAgICBldmVudC5wcmV2ZW50RGVmYXVsdCgpO1xuXG4gICAgY29uc3QgbmV3SW5kZXggPSBOdW1iZXIoZXZlbnQudGFyZ2V0LmdldEF0dHJpYnV0ZSgnZGF0YS1pbmRleCcpKTtcblxuICAgIHRvZ2dsZUN1cnJlbnREb3QobmV3SW5kZXgpO1xuICAgIHBhcmFtcy5oYW5kbGVQcm9ncmVzc0RvdENsaWNrPy4oZXZlbnQpO1xuICB9O1xuXG4gIGNvbnN0IG9uS2V5RG93biA9IChldmVudCkgPT4ge1xuICAgIHN3aXRjaCAoZXZlbnQuY29kZSkge1xuICAgICAgY2FzZSAnRW50ZXInOlxuICAgICAgY2FzZSAnU3BhY2UnOlxuICAgICAgICBvblByb2dyZXNzRG90Q2xpY2soZXZlbnQpO1xuICAgICAgICBicmVhaztcblxuICAgICAgY2FzZSAnQXJyb3dMZWZ0JzpcbiAgICAgIGNhc2UgJ0Fycm93VXAnOlxuICAgICAgICAvLyBHbyB0byBwcmV2aW91cyBkb3RcbiAgICAgICAgc2V0QWN0aXZlRG90KGFjdGl2ZUluZGV4IC0gMSk7XG4gICAgICAgIGJyZWFrO1xuXG4gICAgICBjYXNlICdBcnJvd1JpZ2h0JzpcbiAgICAgIGNhc2UgJ0Fycm93RG93bic6XG4gICAgICAgIC8vIEdvIHRvIG5leHQgZG90XG4gICAgICAgIHNldEFjdGl2ZURvdChhY3RpdmVJbmRleCArIDEpO1xuICAgICAgICBicmVhaztcblxuICAgICAgZGVmYXVsdDpcbiAgICAgICAgYnJlYWs7XG4gICAgfVxuICB9O1xuXG4gIGNvbnN0IGhhc09uZUZvY3VzYWJsZURvdCA9IHBhcmFtcy5kb3RzLnNvbWUoKGRvdCkgPT4gZG90LnRhYkluZGV4ID49IDApO1xuXG4gIHBhcmFtcy5kb3RzLmZvckVhY2goKGRvdCwgaSkgPT4ge1xuICAgIGNvbnN0IGl0ZW0gPSBjcmVhdGVFbGVtZW50KCdsaScsIHtcbiAgICAgIGNsYXNzTmFtZTogJ2g1cC1wcm9ncmVzcy1pdGVtJyxcbiAgICB9KTtcbiAgICAvLyBXZSBuZWVkIHRvIGVuc3VyZSB0aGF0IHdlIGNhbiBrZXlib2FyZCBuYXZpZ2F0ZSB0byBhdCBsZWFzdCBvbmUgb2YgdGhlIGRvdHNcbiAgICBsZXQgdGFiSW5kZXg7XG4gICAgaWYgKGhhc09uZUZvY3VzYWJsZURvdCkge1xuICAgICAgdGFiSW5kZXggPSBkb3QudGFiSW5kZXggPz8gLTE7XG4gICAgfVxuICAgIGVsc2UgaWYgKGkgPT09IDApIHtcbiAgICAgIHRhYkluZGV4ID0gMDtcbiAgICB9XG4gICAgZWxzZSB7XG4gICAgICB0YWJJbmRleCA9IC0xO1xuICAgIH1cbiAgICBjb25zdCBwcm9ncmVzc0RvdCA9IGNyZWF0ZUVsZW1lbnQoJ2EnLCB7XG4gICAgICBocmVmOiAnIycsXG4gICAgICBjbGFzc05hbWU6IGBoNXAtcHJvZ3Jlc3MtZG90IHVuYW5zd2VyZWQgJHt0YWJJbmRleCA+PSAwID8gJ2N1cnJlbnQnIDogJyd9YCxcbiAgICAgIGFyaWFMYWJlbDogZG90LmFyaWFMYWJlbCxcbiAgICAgIHRhYkluZGV4LFxuICAgICAgb25jbGljazogb25Qcm9ncmVzc0RvdENsaWNrLFxuICAgICAgb25rZXlkb3duOiBvbktleURvd24sXG4gICAgfSk7XG5cbiAgICBwcm9ncmVzc0RvdC5zZXRBdHRyaWJ1dGUoJ2RhdGEtaW5kZXgnLCBpKTtcbiAgICBpdGVtLmFwcGVuZENoaWxkKHByb2dyZXNzRG90KTtcbiAgICBkb3RzQ29udGFpbmVyLmFwcGVuZENoaWxkKGl0ZW0pO1xuICAgIHByb2dyZXNzRG90RWxlbWVudHMucHVzaChwcm9ncmVzc0RvdCk7XG4gIH0pO1xuXG4gIGNvbnN0IHNldEFjdGl2ZURvdCA9IChuZXdJbmRleCwgcGxhY2VGb2N1cyA9IHRydWUpID0+IHtcbiAgICBpZiAobmV3SW5kZXggPCAwIHx8IG5ld0luZGV4ID49IHByb2dyZXNzTGVuZ3RoKSB7XG4gICAgICByZXR1cm47XG4gICAgfVxuICAgIGFjdGl2ZUluZGV4ID0gbmV3SW5kZXg7XG4gICAgcHJvZ3Jlc3NEb3RFbGVtZW50cy5mb3JFYWNoKChlbCwgaSkgPT4ge1xuICAgICAgZWwuc2V0QXR0cmlidXRlKCd0YWJJbmRleCcsIGFjdGl2ZUluZGV4ID09PSBpID8gMCA6IC0xKTtcbiAgICB9KTtcblxuICAgIGlmIChwbGFjZUZvY3VzKSB7XG4gICAgICBwcm9ncmVzc0RvdEVsZW1lbnRzW2FjdGl2ZUluZGV4XS5mb2N1cygpO1xuICAgIH1cbiAgfTtcblxuICBjb25zdCB0b2dnbGVDdXJyZW50RG90ID0gKG5ld0luZGV4KSA9PiB7XG4gICAgY29uc3QgeyB0ZXh0cyB9ID0gcGFyYW1zO1xuICAgIHByb2dyZXNzRG90RWxlbWVudHMuZm9yRWFjaCgoZWwsIGkpID0+IHtcbiAgICAgIGVsLnNldEF0dHJpYnV0ZSgndGFiSW5kZXgnLCBhY3RpdmVJbmRleCA9PT0gaSA/IDAgOiAtMSk7XG4gICAgICBjb25zdCBpc0N1cnJlbnQgPSBpID09PSBuZXdJbmRleDtcbiAgICAgIGxldCBsYWJlbCA9IHRleHRzLmp1bXBUb1F1ZXN0aW9uXG4gICAgICAgIC5yZXBsYWNlKCclZCcsIChuZXdJbmRleCArIDEpLnRvU3RyaW5nKCkpXG4gICAgICAgIC5yZXBsYWNlKCcldG90YWwnLCBwcm9ncmVzc0RvdEVsZW1lbnRzLmxlbmd0aCk7XG5cbiAgICAgIGlmICghaXNDdXJyZW50KSB7XG4gICAgICAgIGNvbnN0IGlzQW5zd2VyZWQgPSBlbC5jbGFzc0xpc3QuY29udGFpbnMoJ2Fuc3dlcmVkJyk7XG4gICAgICAgIGxhYmVsICs9IGAsICR7KGlzQW5zd2VyZWQgPyB0ZXh0cy5hbnN3ZXJlZFRleHQgOiB0ZXh0cy51bmFuc3dlcmVkVGV4dCl9YDtcbiAgICAgIH1cbiAgICAgIGVsc2Uge1xuICAgICAgICBsYWJlbCArPSBgLCAke3RleHRzLmN1cnJlbnRRdWVzdGlvblRleHR9YDtcbiAgICAgIH1cblxuICAgICAgZWwuY2xhc3NMaXN0LnRvZ2dsZSgnY3VycmVudCcsIGlzQ3VycmVudCk7XG4gICAgICBlbC5zZXRBdHRyaWJ1dGUoJ2FyaWEtbGFiZWwnLCBsYWJlbCk7XG4gICAgfSk7XG4gIH07XG5cbiAgY29uc3QgdG9nZ2xlRmlsbGVkRG90ID0gKGZpbGxlZEluZGV4LCBpc0ZpbGxlZCkgPT4ge1xuICAgIGNvbnN0IGxhYmVsID0gYCR7cGFyYW1zLnRleHRzLmp1bXBUb1F1ZXN0aW9uXG4gICAgICAucmVwbGFjZSgnJWQnLCAoZmlsbGVkSW5kZXggKyAxKS50b1N0cmluZygpKVxuICAgICAgLnJlcGxhY2UoJyV0b3RhbCcsIHByb2dyZXNzRG90RWxlbWVudHMubGVuZ3RoKVxuICAgIH0sICR7XG4gICAgICBpc0ZpbGxlZCA/IHBhcmFtcy50ZXh0cy5hbnN3ZXJlZFRleHQgOiBwYXJhbXMudGV4dHMudW5hbnN3ZXJlZFRleHR9YDtcblxuICAgIHByb2dyZXNzRG90RWxlbWVudHNbZmlsbGVkSW5kZXhdLmNsYXNzTGlzdC50b2dnbGUoJ3VuYW5zd2VyZWQnLCAhaXNGaWxsZWQpO1xuICAgIHByb2dyZXNzRG90RWxlbWVudHNbZmlsbGVkSW5kZXhdLmNsYXNzTGlzdC50b2dnbGUoJ2Fuc3dlcmVkJywgaXNGaWxsZWQpO1xuICAgIHByb2dyZXNzRG90RWxlbWVudHNbZmlsbGVkSW5kZXhdLnNldEF0dHJpYnV0ZSgnYXJpYS1sYWJlbCcsIGxhYmVsKTtcbiAgfTtcblxuICBkb3RzQ29udGFpbmVyLnNldEFjdGl2ZURvdCA9IHNldEFjdGl2ZURvdDtcbiAgZG90c0NvbnRhaW5lci50b2dnbGVGaWxsZWREb3QgPSB0b2dnbGVGaWxsZWREb3Q7XG4gIGRvdHNDb250YWluZXIudG9nZ2xlQ3VycmVudERvdCA9IHRvZ2dsZUN1cnJlbnREb3Q7XG5cbiAgcmV0dXJuIGRvdHNDb250YWluZXI7XG59XG5cbmV4cG9ydCBkZWZhdWx0IFByb2dyZXNzRG90cztcbiIsIi8qIGVzbGludC1kaXNhYmxlIG5vLXBhcmFtLXJlYXNzaWduICovXG4vKiBlc2xpbnQtZGlzYWJsZSBuby1uZXN0ZWQtdGVybmFyeSAqL1xuaW1wb3J0ICcuLi9zdHlsZXMvaDVwLW5hdmlnYXRpb24uY3NzJztcbmltcG9ydCB7IGNyZWF0ZUVsZW1lbnQgfSBmcm9tICcuLi91dGlscy5qcyc7XG5pbXBvcnQgQnV0dG9uIGZyb20gJy4vaDVwLWJ1dHRvbi5qcyc7XG5pbXBvcnQgUHJvZ3Jlc3NCYXIgZnJvbSAnLi9oNXAtcHJvZ3Jlc3MtYmFyLmpzJztcbmltcG9ydCBQcm9ncmVzc0RvdHMgZnJvbSAnLi9oNXAtcHJvZ3Jlc3MtZG90cy5qcyc7XG5cbi8qKlxuICogQHR5cGVkZWYgTmF2aWdhdGlvblRleHRzXG4gKiBAdHlwZSB7b2JqZWN0fVxuICogQHByb3BlcnR5IHtzdHJpbmd9IHByZXZpb3VzQnV0dG9uXG4gKiBAcHJvcGVydHkge3N0cmluZ30gbmV4dEJ1dHRvblxuICogQHByb3BlcnR5IHtzdHJpbmd9IGxhc3RCdXR0b25cbiAqIEBwcm9wZXJ0eSB7W3N0cmluZ119IHByZXZpb3VzQnV0dG9uQXJpYVxuICogQHByb3BlcnR5IHtbc3RyaW5nXX0gbmV4dEJ1dHRvbkFyaWFcbiAqIEBwcm9wZXJ0eSB7W3N0cmluZ119IGxhc3RCdXR0b25BcmlhXG4gKiBAcHJvcGVydHkge1tzdHJpbmddfSBwcmV2aW91c1Rvb2x0aXBcbiAqIEBwcm9wZXJ0eSB7W3N0cmluZ119IG5leHRUb29sdGlwXG4gKiBAcHJvcGVydHkge1tzdHJpbmddfSBsYXN0VG9vbHRpcFxuICogQHByb3BlcnR5IHtbc3RyaW5nXX0gY3VycmVudFRvb2x0aXBcbiAqIEBwcm9wZXJ0eSB7W3N0cmluZ119IHRvdGFsVG9vbHRpcFxuICogVGhlIGl0ZW1zIGJlbG93IGFyZSB1c2VkIGJ5IFByb2dyZXNzRG90c1xuICogQHByb3BlcnR5IHtzdHJpbmd9IGp1bXBUb1F1ZXN0aW9uXG4gKiBAcHJvcGVydHkge3N0cmluZ30gYW5zd2VyZWRUZXh0XG4gKiBAcHJvcGVydHkge3N0cmluZ30gdW5hbnN3ZXJlZFRleHRcbiAqIFRoZSBpdGVtIGJlbG93IGlzIHVzZWQgYnkgUHJvZ3Jlc3NUZXh0XG4gKiBAcHJvcGVydHkge3N0cmluZ30gdGV4dHVhbFByb2dyZXNzXG4gKi9cblxuLyoqXG4gKiBAdHlwZWRlZiB7JzMtc3BsaXQnIHwgJzItc3BsaXQtbmV4dCcgfCAnMi1zcGxpdC1zcHJlYWQnfSBOYXZpZ2F0aW9uVmFyaWFudFxuICogQHR5cGVkZWYgeydiYXInIHwgJ2RvdHMnIHwgJ3RleHQnfSBOYXZpZ2F0aW9uUHJvZ3Jlc3NUeXBlXG4gKi9cblxuLyoqXG4gKiBAdHlwZWRlZiBOYXZpZ2F0aW9uUGFyYW1zXG4gKiBAdHlwZSB7b2JqZWN0fVxuICogQHByb3BlcnR5IHtudW1iZXJ9IGluZGV4IFRoZSBjdXJyZW50IHBvc2l0aW9uIGluIHRoZSBuYXZpZ2F0aW9uXG4gKiBAcHJvcGVydHkge251bWJlcn0gbmF2aWdhdGlvbkxlbmd0aCBUaGUgbnVtYmVyIG9mIFwiaXRlbXNcIiB3ZSBjYW4gbmF2aWdhdGUgdGhyb3VnaFxuICogQHByb3BlcnR5IHtbTmF2aWdhdGlvblZhcmlhbnRdfSB2YXJpYW50XG4gKiAgICBUaGUgdHlwZSBvZiBncmlkIGxheW91dCBmb3IgdGhlIG5hdmlnYXRpb24gKDNzcGxpdCBpcyBkZWZhdWx0KVxuICogQHByb3BlcnR5IHtbTmF2aWdhdGlvblRleHRzXX0gdGV4dHNcbiAqICAgIFRyYW5zbGF0aW9ucyBzdHVmZi4gQHRvZG8sIHNob3VsZCBINVAuQ29tcG9uZW50IG1haW50YWluIG93biB0cmFuc2xhdGlvbnM/XG4gKiBAcHJvcGVydHkge1tzdHJpbmddfSBjbGFzc05hbWUgRXh0cmEgY3NzIGNsYXNzZXMgdG8gYmUgYXBwbGllZCBvbiB0aGUgbmF2aWdhdGlvbiBlbGVtZW50XG4gKiBAcHJvcGVydHkge1tmdW5jdGlvbl19IGhhbmRsZVByZXZpb3VzXG4gKiAgICBBIGZ1bmN0aW9uIHRoYXQgZW5hYmxlcyB0aGUgcHJldmlvdXMgYnV0dG9uIGFuZCB0cmlnZ2VycyB3aGVuIGl0IGhhcyBiZWVuIGNsaWNrZWRcbiAqIEBwcm9wZXJ0eSB7W2Z1bmN0aW9uXX0gaGFuZGxlTmV4dFxuICogICAgQSBmdW5jdGlvbiB0aGF0IGVuYWJsZXMgdGhlIG5leHQgYnV0dG9uIGFuZCB0cmlnZ2VycyB3aGVuIGl0IGhhcyBiZWVuIGNsaWNrZWRcbiAqIEBwcm9wZXJ0eSB7W2Z1bmN0aW9uXX0gaGFuZGxlTGFzdFxuICogICAgQSBmdW5jdGlvbiB0aGF0IGVuYWJsZXMgdGhlIFwibGFzdFwiIGJ1dHRvbiBhbmQgdHJpZ2dlcnMgd2hlbiBpdCBoYXMgYmVlbiBjbGlja2VkXG4gKiAgICBUeXBpY2FsbHkgYSBcInN1Ym1pdFwiIG9yIFwic2hvdyByZXN1bHRzXCIgYnV0dG9uXG4gKiBAcHJvcGVydHkge1tOYXZpZ2F0aW9uUHJvZ3Jlc3NUeXBlXX0gcHJvZ3Jlc3NUeXBlXG4gKiAgICBDYW4gc2hvdyBhIHByb2dyZXNzIGJhciwgZG90IG5hdmlnYXRpb24gb3IgdGV4dHVhbCBwcm9ncmVzc1xuICogQHByb3BlcnR5IHtbQXJyYXldfSBkb3RzXG4gKiAgICBJZiBwcm9ncmVzc1R5cGU9PT0nZG90cycsIHRoZSBkb3RzIGFycmF5IGlzIHJlcXVpcmVkXG4gKiAgICBFYWNoIGRvdCBoYXMgdGFiSW5kZXggYW5kIGFyaWFMYWJlbCBwcm9wZXJ0eVxuICogQHByb3BlcnR5IHtbZnVuY3Rpb25dfSBoYW5kbGVQcm9ncmVzc0RvdENsaWNrXG4gKiAgICBBIGZ1bmN0aW9uIHRoYXQgaXMgY2FsbGVkIHdoZW4gdGhlIHVzZXIgY2xpY2tzIHRoZSBvbiBhIFwiZG90XCIuIE9wdGlvbmFsXG4gKiBAcHJvcGVydHkge1tvYmplY3RdfSBvcHRpb25zXG4gKiBAcHJvcGVydHkge1tib29sZWFuXX0gb3B0aW9ucy5kaXNhYmxlQmFja3dhcmRzTmF2aWdhdGlvblxuICogICAgSWYgYmFja3dhcmRzIG5hdmlnYXRpb24gc2hvdWxkIGJlIGRpc2FibGVkIG9yIG5vdFxuICogQHByb3BlcnR5IHtbYm9vbGVhbl19IHNob3dEaXNhYmxlZEJ1dHRvbnNcbiAqICAgIElmIHRydWUsIGJ1dHRvbnMgd2lsbCBiZSBkaXNhYmxlZCBpbnN0ZWFkIG9mIGhpZGRlbiB3aGVuIG5vdCB1c2FibGVcbiAqICBAcHJvcGVydHkge1tBcnJheV19IHRpdGxlc1xuICogICAgQXJyYXkgb2YgdGl0bGVzIGZvciBlYWNoIHBhZ2UvY2hhcHRlciwgdXNlZCB3aGVuIHByb2dyZXNzVHlwZSBpcyAndGV4dCdcbiAqL1xuXG4vKipcbiAqIENyZWF0ZSBET00gZWxlbWVudHMgZnJvbSB0ZXh0IHdpdGggcGxhY2Vob2xkZXJzXG4gKiBAcGFyYW0ge3N0cmluZ30gdGV4dCAtIFRleHQgY29udGFpbmluZyBwbGFjZWhvbGRlcnMgbGlrZSBAY3VycmVudCwgQHRvdGFsXG4gKiBAcGFyYW0ge29iamVjdH0gcmVwbGFjZW1lbnRzIC0gT2JqZWN0IG1hcHBpbmcgcGxhY2Vob2xkZXIgbmFtZXMgdG8gcmVwbGFjZW1lbnQgZnVuY3Rpb25zXG4gKiBAcmV0dXJucyB7W05vZGVdfSBBcnJheSBvZiBET00gbm9kZXMgKHRleHQgbm9kZXMgYW5kIGVsZW1lbnRzKVxuICovXG5mdW5jdGlvbiBjcmVhdGVFbGVtZW50c0Zyb21QbGFjZWhvbGRlcnModGV4dCwgcmVwbGFjZW1lbnRzKSB7XG4gIGNvbnN0IHBsYWNlaG9sZGVycyA9IE9iamVjdC5rZXlzKHJlcGxhY2VtZW50cyk7XG4gIGNvbnN0IHJlZ0V4cCA9IG5ldyBSZWdFeHAoYCgke3BsYWNlaG9sZGVycy5tYXAoKHApID0+IHAucmVwbGFjZSgvWy4qKz9eJHt9KCl8W1xcXVxcXFxdL2csICdcXFxcJCYnKSkuam9pbignfCcpfSlgLCAnZycpO1xuXG4gIHJldHVybiB0ZXh0LnNwbGl0KHJlZ0V4cClcbiAgICAuZmlsdGVyKChwYXJ0KSA9PiBwYXJ0ICE9PSAnJylcbiAgICAubWFwKChwYXJ0KSA9PiAocmVwbGFjZW1lbnRzW3BhcnRdID8gcmVwbGFjZW1lbnRzW3BhcnRdKCkgOiBkb2N1bWVudC5jcmVhdGVUZXh0Tm9kZShwYXJ0KSkpO1xufVxuXG4vKipcbiAqIENyZWF0ZSBhIHNwYW4gZWxlbWVudCB3aXRoIG9wdGlvbmFsIHRvb2x0aXBcbiAqIEBwYXJhbSB7c3RyaW5nfSBjbGFzc05hbWUgLSBDU1MgY2xhc3MgbmFtZSBmb3IgdGhlIHNwYW5cbiAqIEBwYXJhbSB7c3RyaW5nfG51bWJlcn0gY29udGVudCAtIFRleHQgY29udGVudCBmb3IgdGhlIHNwYW5cbiAqIEBwYXJhbSB7c3RyaW5nfSBbdG9vbHRpcFRleHRdIC0gT3B0aW9uYWwgdG9vbHRpcCB0ZXh0XG4gKiBAcmV0dXJucyB7SFRNTEVsZW1lbnR9IFRoZSBzcGFuIGVsZW1lbnRcbiAqL1xuZnVuY3Rpb24gY3JlYXRlUHJvZ3Jlc3NTcGFuKGNsYXNzTmFtZSwgY29udGVudCwgdG9vbHRpcFRleHQpIHtcbiAgY29uc3Qgc3BhbiA9IGNyZWF0ZUVsZW1lbnQoJ3NwYW4nLCB7XG4gICAgY2xhc3NMaXN0OiBjbGFzc05hbWUsXG4gICAgaW5uZXJUZXh0OiBjb250ZW50LFxuICB9KTtcblxuICBpZiAodG9vbHRpcFRleHQpIHtcbiAgICBINVAuVG9vbHRpcChzcGFuLCB7IHRleHQ6IHRvb2x0aXBUZXh0LCBwb3NpdGlvbjogJ3RvcCcgfSk7XG4gIH1cblxuICByZXR1cm4gc3Bhbjtcbn1cblxuLyoqXG4gKiBVcGRhdGUgcHJvZ3Jlc3MgdGV4dCBlbGVtZW50IHdpdGggbmV3IGN1cnJlbnQvdG90YWwgdmFsdWVzXG4gKiBAcGFyYW0ge0hUTUxFbGVtZW50fSBwcm9ncmVzc1RleHQgLSBFeGlzdGluZyBwcm9ncmVzcyB0ZXh0IGVsZW1lbnQgdG8gdXBkYXRlXG4gKiBAcGFyYW0ge3N0cmluZ30gdGV4dHVhbFByb2dyZXNzIC0gVGV4dCB0ZW1wbGF0ZSB3aXRoIEBjdXJyZW50IGFuZCBAdG90YWwgcGxhY2Vob2xkZXJzXG4gKiBAcGFyYW0ge251bWJlcn0gY3VycmVudEluZGV4IC0gQ3VycmVudCBpbmRleCAoMC1iYXNlZClcbiAqIEBwYXJhbSB7bnVtYmVyfSBuYXZpZ2F0aW9uTGVuZ3RoIC0gVG90YWwgbnVtYmVyIG9mIGl0ZW1zXG4gKiBAcGFyYW0ge29iamVjdH0gdGV4dHMgLSBUZXh0IGNvbmZpZ3VyYXRpb24gb2JqZWN0XG4gKiBAcGFyYW0ge3N0cmluZ30gW3BhcmFtcy50ZXh0cy5jdXJyZW50VG9vbHRpcF0gLSBUb29sdGlwIGZvciBjdXJyZW50IGluZGV4XG4gKiBAcGFyYW0ge3N0cmluZ30gW3BhcmFtcy50ZXh0cy50b3RhbFRvb2x0aXBdIC0gVG9vbHRpcCBmb3IgdG90YWwgY291bnQqXG4gKi9cbi8vIGVzbGludC1kaXNhYmxlLW5leHQtbGluZSBtYXgtbGVuXG5mdW5jdGlvbiB1cGRhdGVQcm9ncmVzc1RleHQocHJvZ3Jlc3NUZXh0LCB0ZXh0dWFsUHJvZ3Jlc3MsIGN1cnJlbnRJbmRleCwgbmF2aWdhdGlvbkxlbmd0aCwgdGV4dHMgPSB7fSkge1xuICAvLyBDbGVhciBleGlzdGluZyBjb250ZW50XG4gIHByb2dyZXNzVGV4dC5pbm5lckhUTUwgPSAnJztcblxuICAvLyBDcmVhdGUgbmV3IGNvbnRlbnRcbiAgY29uc3QgZG9tUGFydHMgPSBjcmVhdGVFbGVtZW50c0Zyb21QbGFjZWhvbGRlcnModGV4dHVhbFByb2dyZXNzLCB7XG4gICAgJ0BjdXJyZW50JzogKCkgPT4gY3JlYXRlUHJvZ3Jlc3NTcGFuKCdwcm9ncmVzcy1jdXJyZW50JywgY3VycmVudEluZGV4ICsgMSwgdGV4dHMuY3VycmVudFRvb2x0aXApLFxuICAgICdAdG90YWwnOiAoKSA9PiBjcmVhdGVQcm9ncmVzc1NwYW4oJ3Byb2dyZXNzLWxhc3QnLCBuYXZpZ2F0aW9uTGVuZ3RoLCB0ZXh0cy50b3RhbFRvb2x0aXApLFxuICB9KTtcblxuICBkb21QYXJ0cy5mb3JFYWNoKChwYXJ0KSA9PiBwcm9ncmVzc1RleHQuYXBwZW5kQ2hpbGQocGFydCkpO1xufVxuXG4vKipcbiAqIENyZWF0ZSBhIHByb2dyZXNzIHRleHQgZWxlbWVudCB3aXRoIGN1cnJlbnQvdG90YWwgcGxhY2Vob2xkZXJzXG4gKiBAcGFyYW0ge29iamVjdH0gcGFyYW1zIC0gUGFyYW1ldGVycyBmb3IgY3JlYXRpbmcgcHJvZ3Jlc3MgdGV4dFxuICogQHBhcmFtIHtzdHJpbmd9IHBhcmFtcy50ZXh0dWFsUHJvZ3Jlc3MgLSBUZXh0IHRlbXBsYXRlIHdpdGggQGN1cnJlbnQgYW5kIEB0b3RhbCBwbGFjZWhvbGRlcnNcbiAqIEBwYXJhbSB7bnVtYmVyfSBwYXJhbXMuY3VycmVudEluZGV4IC0gQ3VycmVudCBpbmRleCAoMC1iYXNlZClcbiAqIEBwYXJhbSB7bnVtYmVyfSBwYXJhbXMubmF2aWdhdGlvbkxlbmd0aCAtIFRvdGFsIG51bWJlciBvZiBpdGVtc1xuICogQHBhcmFtIHtvYmplY3R9IHBhcmFtcy50ZXh0cyAtIFRleHQgY29uZmlndXJhdGlvbiBvYmplY3RcbiAqIEBwYXJhbSB7c3RyaW5nfSBbcGFyYW1zLnRleHRzLmN1cnJlbnRUb29sdGlwXSAtIFRvb2x0aXAgZm9yIGN1cnJlbnQgaW5kZXhcbiAqIEBwYXJhbSB7c3RyaW5nfSBbcGFyYW1zLnRleHRzLnRvdGFsVG9vbHRpcF0gLSBUb29sdGlwIGZvciB0b3RhbCBjb3VudFxuICogQHJldHVybnMge0hUTUxFbGVtZW50fSBUaGUgY29tcGxldGUgcHJvZ3Jlc3NUZXh0IGVsZW1lbnRcbiAqL1xuZnVuY3Rpb24gY3JlYXRlUHJvZ3Jlc3NUZXh0KHtcbiAgdGV4dHVhbFByb2dyZXNzLCBjdXJyZW50SW5kZXgsIG5hdmlnYXRpb25MZW5ndGgsIHRleHRzID0ge30sXG59KSB7XG4gIGNvbnN0IHByb2dyZXNzVGV4dCA9IGNyZWF0ZUVsZW1lbnQoJ2RpdicsIHtcbiAgICBjbGFzc0xpc3Q6ICdwcm9ncmVzcy10ZXh0JyxcbiAgfSk7XG5cbiAgdXBkYXRlUHJvZ3Jlc3NUZXh0KHByb2dyZXNzVGV4dCwgdGV4dHVhbFByb2dyZXNzLCBjdXJyZW50SW5kZXgsIG5hdmlnYXRpb25MZW5ndGgsIHRleHRzKTtcblxuICByZXR1cm4gcHJvZ3Jlc3NUZXh0O1xufVxuXG4vKipcbiAqIENyZWF0ZSBhIG5hdmlnYXRpb24gY29tcG9uZW50LCB3aXRoIG9wdGlvbmFsIHByb2dyZXNzIGNvbXBvbmVudHMuXG4gKiBAcGFyYW0ge05hdmlnYXRpb25QYXJhbXN9IHBhcmFtcyBBIHNldCBvZiBwYXJhbWV0ZXJzIHRvIGNvbmZpZ3VyZSB0aGUgTmF2aWdhdGlvbiBjb21wb25lbnRcbiAqIEByZXR1cm5zIHtIVE1MRWxlbWVudH0gVGhlIG5hdmlnYXRpb24gZWxlbWVudFxuICovXG5mdW5jdGlvbiBOYXZpZ2F0aW9uKHBhcmFtcyA9IHt9KSB7XG4gIGxldCBwcm9ncmVzc0JhcjtcbiAgbGV0IGRvdHNOYXZpZ2F0aW9uO1xuICBsZXQgcHJvZ3Jlc3NUZXh0O1xuICBsZXQgdGl0bGU7XG4gIGxldCBwcmV2QnV0dG9uO1xuICBsZXQgbmV4dEJ1dHRvbjtcbiAgbGV0IGxhc3RCdXR0b247XG4gIGxldCBjYW5TaG93TGFzdCA9IGZhbHNlO1xuICBsZXQgaW5kZXggPSBwYXJhbXMuaW5kZXggPz8gMDtcbiAgbGV0IGNsYXNzTmFtZSA9ICdoNXAtbmF2aWdhdGlvbic7XG5cbiAgaWYgKHBhcmFtcy52YXJpYW50ID09PSAnMi1zcGxpdC1zcHJlYWQnKSB7XG4gICAgY2xhc3NOYW1lICs9ICcgaDVwLW5hdmlnYXRpb24tLTItc3BsaXQtc3ByZWFkJztcbiAgfVxuICBlbHNlIGlmIChwYXJhbXMudmFyaWFudCA9PT0gJzItc3BsaXQtbmV4dCcpIHtcbiAgICBjbGFzc05hbWUgKz0gJyBoNXAtbmF2aWdhdGlvbi0tMi1zcGxpdC1uZXh0JztcbiAgfVxuICBlbHNlIHtcbiAgICBjbGFzc05hbWUgKz0gJyBoNXAtbmF2aWdhdGlvbi0tMy1zcGxpdCc7XG4gIH1cblxuICBjb25zdCBjb250YWluZXIgPSBjcmVhdGVFbGVtZW50KCduYXYnLCB7XG4gICAgY2xhc3NMaXN0OiBgJHtjbGFzc05hbWV9ICR7cGFyYW1zLmNsYXNzTmFtZSA/PyAnJ31gLFxuICAgIHJvbGU6ICduYXZpZ2F0aW9uJyxcbiAgfSk7XG5cbiAgaWYgKHBhcmFtcy5oYW5kbGVQcmV2aW91cykge1xuICAgIGNvbnN0IHByZXZDbGFzc0xpc3QgPSAnaDVwLXRoZW1lLXByZXZpb3VzJztcbiAgICBwcmV2QnV0dG9uID0gQnV0dG9uKHtcbiAgICAgIHN0eWxlVHlwZTogJ25hdicsXG4gICAgICBsYWJlbDogcGFyYW1zPy50ZXh0cz8ucHJldmlvdXNCdXR0b24gPz8gJ1ByZXZpb3VzJyxcbiAgICAgIGFyaWFMYWJlbDogcGFyYW1zPy50ZXh0cy5wcmV2aW91c0J1dHRvbkFyaWEsXG4gICAgICB0b29sdGlwOiBwYXJhbXM/LnRleHRzLnByZXZpb3VzVG9vbHRpcCxcbiAgICAgIGljb246ICdwcmV2aW91cycsXG4gICAgICBjbGFzc2VzOlxuICAgICAgICAvLyBlc2xpbnQtZGlzYWJsZS1uZXh0LWxpbmUgbm8tbmVzdGVkLXRlcm5hcnlcbiAgICAgICAgaW5kZXggPT09IDBcbiAgICAgICAgICA/IHBhcmFtcy5zaG93RGlzYWJsZWRCdXR0b25zXG4gICAgICAgICAgICA/IGAke3ByZXZDbGFzc0xpc3R9IGg1cC1kaXNhYmxlZGBcbiAgICAgICAgICAgIDogYCR7cHJldkNsYXNzTGlzdH0gaDVwLXZpc2liaWxpdHktaGlkZGVuYFxuICAgICAgICAgIDogcHJldkNsYXNzTGlzdCxcbiAgICAgIGRpc2FibGVkOiBwYXJhbXMuc2hvd0Rpc2FibGVkQnV0dG9ucyAmJiBpbmRleCA9PT0gMCxcbiAgICAgIG9uQ2xpY2s6IChldmVudCkgPT4ge1xuICAgICAgICBpZiAocGFyYW1zLmhhbmRsZVByZXZpb3VzKGV2ZW50KSAhPT0gZmFsc2UpIHtcbiAgICAgICAgICBwcmV2aW91cygpO1xuICAgICAgICB9XG4gICAgICB9LFxuICAgIH0pO1xuICAgIGNvbnRhaW5lci5hcHBlbmRDaGlsZChwcmV2QnV0dG9uKTtcbiAgfVxuXG4gIGlmIChwYXJhbXMucHJvZ3Jlc3NUeXBlID09PSAnYmFyJykge1xuICAgIHByb2dyZXNzQmFyID0gUHJvZ3Jlc3NCYXIoe1xuICAgICAgaW5kZXgsXG4gICAgICBwcm9ncmVzc0xlbmd0aDogcGFyYW1zLm5hdmlnYXRpb25MZW5ndGgsXG4gICAgfSk7XG4gICAgY29udGFpbmVyLmFwcGVuZENoaWxkKHByb2dyZXNzQmFyKTtcbiAgfVxuICBlbHNlIGlmIChwYXJhbXMucHJvZ3Jlc3NUeXBlID09PSAnZG90cycpIHtcbiAgICBkb3RzTmF2aWdhdGlvbiA9IFByb2dyZXNzRG90cyh7XG4gICAgICBkb3RzOiBwYXJhbXMuZG90cyxcbiAgICAgIHRleHRzOiBwYXJhbXMudGV4dHMgPz8ge30sXG4gICAgICBoYW5kbGVQcm9ncmVzc0RvdENsaWNrOiAoZXZlbnQpID0+IHtcbiAgICAgICAgaW5kZXggPSBOdW1iZXIoZXZlbnQudGFyZ2V0LmdldEF0dHJpYnV0ZSgnZGF0YS1pbmRleCcpKTtcbiAgICAgICAgcGFyYW1zLmhhbmRsZVByb2dyZXNzRG90Q2xpY2s/LihldmVudCwgaW5kZXgpO1xuICAgICAgfSxcbiAgICB9KTtcbiAgICBjb250YWluZXIuYXBwZW5kQ2hpbGQoZG90c05hdmlnYXRpb24pO1xuICB9XG4gIGVsc2UgaWYgKHBhcmFtcy5wcm9ncmVzc1R5cGUgPT09ICd0ZXh0Jykge1xuICAgIGNvbnN0IHByb2dyZXNzQ29udGFpbmVyID0gY3JlYXRlRWxlbWVudCgnZGl2Jywge1xuICAgICAgY2xhc3NMaXN0OiAncHJvZ3Jlc3MtY29udGFpbmVyIGg1cC10aGVtZS1wcm9ncmVzcycsXG4gICAgfSk7XG5cbiAgICBwcm9ncmVzc1RleHQgPSBjcmVhdGVQcm9ncmVzc1RleHQoe1xuICAgICAgdGV4dHVhbFByb2dyZXNzOiBwYXJhbXMudGV4dHMudGV4dHVhbFByb2dyZXNzLFxuICAgICAgY3VycmVudEluZGV4OiBpbmRleCxcbiAgICAgIG5hdmlnYXRpb25MZW5ndGg6IHBhcmFtcy5uYXZpZ2F0aW9uTGVuZ3RoLFxuICAgICAgdGV4dHM6IHBhcmFtcy50ZXh0cyxcbiAgICB9KTtcblxuICAgIHByb2dyZXNzQ29udGFpbmVyLmFwcGVuZENoaWxkKHByb2dyZXNzVGV4dCk7XG5cbiAgICAvLyBQYWdlIGNoYXB0ZXIgdGl0bGUgdXNlZCBpbiBJQlxuICAgIGlmIChwYXJhbXMudGl0bGVzICYmIHBhcmFtcy50aXRsZXMubGVuZ3RoID4gMCkge1xuICAgICAgdGl0bGUgPSBjcmVhdGVFbGVtZW50KCdoMScsIHtcbiAgICAgICAgY2xhc3NMaXN0OiAndGl0bGUnLFxuICAgICAgfSk7XG4gICAgICB0aXRsZS50ZXh0Q29udGVudCA9IHBhcmFtcy50aXRsZXNbaW5kZXhdIHx8ICcnO1xuXG4gICAgICBjb25zdCBwcm9ncmVzc1dyYXBwZXIgPSBjcmVhdGVFbGVtZW50KCdkaXYnLCB7XG4gICAgICAgIGNsYXNzTGlzdDogJ3Byb2dyZXNzLXdyYXBwZXInLFxuICAgICAgfSk7XG4gICAgICBwcm9ncmVzc1dyYXBwZXIuYXBwZW5kQ2hpbGQocHJvZ3Jlc3NDb250YWluZXIpO1xuICAgICAgcHJvZ3Jlc3NXcmFwcGVyLmFwcGVuZENoaWxkKHRpdGxlKTtcbiAgICAgIGNvbnRhaW5lci5hcHBlbmRDaGlsZChwcm9ncmVzc1dyYXBwZXIpO1xuICAgIH1cbiAgICBlbHNlIHtcbiAgICAgIGNvbnRhaW5lci5hcHBlbmRDaGlsZChwcm9ncmVzc0NvbnRhaW5lcik7XG4gICAgfVxuICB9XG5cbiAgaWYgKHBhcmFtcy5oYW5kbGVOZXh0KSB7XG4gICAgY29uc3QgbmV4dENsYXNzTGlzdCA9ICdoNXAtdGhlbWUtbmV4dCc7XG4gICAgbmV4dEJ1dHRvbiA9IEJ1dHRvbih7XG4gICAgICBzdHlsZVR5cGU6ICduYXYnLFxuICAgICAgbGFiZWw6IHBhcmFtcz8udGV4dHM/Lm5leHRCdXR0b24gPz8gJ05leHQnLFxuICAgICAgYXJpYUxhYmVsOiBwYXJhbXM/LnRleHRzLm5leHRCdXR0b25BcmlhLFxuICAgICAgdG9vbHRpcDogcGFyYW1zPy50ZXh0cy5uZXh0VG9vbHRpcCxcbiAgICAgIGljb246ICduZXh0JyxcbiAgICAgIGNsYXNzZXM6XG4gICAgICAgIGluZGV4ID09PSBwYXJhbXMubmF2aWdhdGlvbkxlbmd0aCAtIDFcbiAgICAgICAgICA/IHBhcmFtcy5zaG93RGlzYWJsZWRCdXR0b25zXG4gICAgICAgICAgICA/IGAke25leHRDbGFzc0xpc3R9IGg1cC1kaXNhYmxlZGBcbiAgICAgICAgICAgIDogYCR7bmV4dENsYXNzTGlzdH0gaDVwLXZpc2liaWxpdHktaGlkZGVuYFxuICAgICAgICAgIDogbmV4dENsYXNzTGlzdCxcbiAgICAgIGRpc2FibGVkOlxuICAgICAgICBwYXJhbXMuc2hvd0Rpc2FibGVkQnV0dG9ucyAmJiBpbmRleCA9PT0gcGFyYW1zLm5hdmlnYXRpb25MZW5ndGggLSAxLFxuICAgICAgb25DbGljazogKGV2ZW50KSA9PiB7XG4gICAgICAgIGlmIChwYXJhbXMuaGFuZGxlTmV4dChldmVudCkgIT09IGZhbHNlKSB7XG4gICAgICAgICAgbmV4dCgpO1xuICAgICAgICB9XG4gICAgICB9LFxuICAgIH0pO1xuICAgIGNvbnRhaW5lci5hcHBlbmRDaGlsZChuZXh0QnV0dG9uKTtcbiAgfVxuXG4gIGlmIChwYXJhbXMuaGFuZGxlTGFzdCkge1xuICAgIGxhc3RCdXR0b24gPSBCdXR0b24oe1xuICAgICAgc3R5bGVUeXBlOiAncHJpbWFyeScsXG4gICAgICBsYWJlbDogcGFyYW1zPy50ZXh0cz8ubGFzdEJ1dHRvbiA/PyAnU3VibWl0JyxcbiAgICAgIGFyaWFMYWJlbDogcGFyYW1zPy50ZXh0cy5sYXN0QnV0dG9uQXJpYSxcbiAgICAgIHRvb2x0aXA6IHBhcmFtcz8udGV4dHMubGFzdFRvb2x0aXAsXG4gICAgICBpY29uOiAnc2hvdy1yZXN1bHRzJyxcbiAgICAgIGNsYXNzZXM6ICdoNXAtdmlzaWJpbGl0eS1oaWRkZW4nLFxuICAgICAgb25DbGljazogKGV2ZW50KSA9PiB7XG4gICAgICAgIG5leHQoKTtcbiAgICAgICAgcGFyYW1zLmhhbmRsZUxhc3QoZXZlbnQpO1xuICAgICAgfSxcbiAgICB9KTtcbiAgICBjb250YWluZXIuYXBwZW5kQ2hpbGQobGFzdEJ1dHRvbik7XG4gIH1cblxuICBjb25zdCBjYWxjdWxhdGVCdXR0b25WaXNpYmlsaXR5ID0gKCkgPT4ge1xuICAgIGlmIChwYXJhbXMuc2hvd0Rpc2FibGVkQnV0dG9ucykge1xuICAgICAgLy8gRGlzYWJsZS9lbmFibGUgYnV0dG9ucyBpbnN0ZWFkIG9mIGhpZGluZyB0aGVtXG4gICAgICBpZiAocHJldkJ1dHRvbikge1xuICAgICAgICBwcmV2QnV0dG9uLnRvZ2dsZUF0dHJpYnV0ZSgnZGlzYWJsZWQnLCBpbmRleCA9PT0gMCk7XG4gICAgICAgIHByZXZCdXR0b24uY2xhc3NMaXN0LnRvZ2dsZSgnaDVwLWRpc2FibGVkJywgaW5kZXggPT09IDApO1xuICAgICAgfVxuXG4gICAgICBpZiAobmV4dEJ1dHRvbikge1xuICAgICAgICBjb25zdCBpc0xhc3RQYWdlID0gaW5kZXggPj0gcGFyYW1zLm5hdmlnYXRpb25MZW5ndGggLSAxO1xuICAgICAgICBuZXh0QnV0dG9uLnRvZ2dsZUF0dHJpYnV0ZSgnZGlzYWJsZWQnLCBpc0xhc3RQYWdlKTtcbiAgICAgICAgbmV4dEJ1dHRvbi5jbGFzc0xpc3QudG9nZ2xlKCdoNXAtZGlzYWJsZWQnLCBpc0xhc3RQYWdlKTtcblxuICAgICAgICAvLyBMYXN0IGJ1dHRvbiBzdGlsbCB1c2VzIHZpc2liaWxpdHkgbG9naWNcbiAgICAgICAgbGFzdEJ1dHRvbj8uY2xhc3NMaXN0LnRvZ2dsZShcbiAgICAgICAgICAnaDVwLXZpc2liaWxpdHktaGlkZGVuJyxcbiAgICAgICAgICAhY2FuU2hvd0xhc3QgfHwgIWlzTGFzdFBhZ2UsXG4gICAgICAgICk7XG4gICAgICB9XG4gICAgfVxuICAgIGVsc2Uge1xuICAgICAgLy8gT3JpZ2luYWwgYmVoYXZpb3IgLSBoaWRlL3Nob3cgYnV0dG9uc1xuICAgICAgaWYgKHByZXZCdXR0b24gJiYgaW5kZXggPT09IDApIHtcbiAgICAgICAgcHJldkJ1dHRvbi5jbGFzc0xpc3QuYWRkKCdoNXAtdmlzaWJpbGl0eS1oaWRkZW4nKTtcbiAgICAgIH1cbiAgICAgIGVsc2UgaWYgKHByZXZCdXR0b24gJiYgaW5kZXggPiAwKSB7XG4gICAgICAgIHByZXZCdXR0b24uY2xhc3NMaXN0LnJlbW92ZSgnaDVwLXZpc2liaWxpdHktaGlkZGVuJyk7XG4gICAgICB9XG5cbiAgICAgIGlmIChuZXh0QnV0dG9uICYmIGluZGV4ID49IHBhcmFtcy5uYXZpZ2F0aW9uTGVuZ3RoIC0gMSkge1xuICAgICAgICBuZXh0QnV0dG9uLmNsYXNzTGlzdC5hZGQoJ2g1cC12aXNpYmlsaXR5LWhpZGRlbicpO1xuICAgICAgICBsYXN0QnV0dG9uPy5jbGFzc0xpc3QudG9nZ2xlKCdoNXAtdmlzaWJpbGl0eS1oaWRkZW4nLCAhY2FuU2hvd0xhc3QpO1xuICAgICAgfVxuICAgICAgZWxzZSBpZiAobmV4dEJ1dHRvbiAmJiBpbmRleCA8IHBhcmFtcy5uYXZpZ2F0aW9uTGVuZ3RoIC0gMSkge1xuICAgICAgICBuZXh0QnV0dG9uLmNsYXNzTGlzdC5yZW1vdmUoJ2g1cC12aXNpYmlsaXR5LWhpZGRlbicpO1xuICAgICAgICBsYXN0QnV0dG9uPy5jbGFzc0xpc3QuYWRkKCdoNXAtdmlzaWJpbGl0eS1oaWRkZW4nKTtcbiAgICAgIH1cbiAgICB9XG4gIH07XG5cbiAgY29uc3Qgc2V0Q2FuU2hvd0xhc3QgPSAoY2FuU2hvdykgPT4ge1xuICAgIGNhblNob3dMYXN0ID0gY2FuU2hvdztcbiAgICBjYWxjdWxhdGVCdXR0b25WaXNpYmlsaXR5KCk7XG4gIH07XG5cbiAgY29uc3Qgc2V0Q3VycmVudEluZGV4ID0gKG5ld0luZGV4KSA9PiB7XG4gICAgaW5kZXggPSBuZXdJbmRleDtcblxuICAgIGlmICh0aXRsZSAmJiBwYXJhbXMudGl0bGVzICYmIHBhcmFtcy50aXRsZXNbaW5kZXhdKSB7XG4gICAgICB0aXRsZS50ZXh0Q29udGVudCA9IHBhcmFtcy50aXRsZXNbaW5kZXhdO1xuICAgIH1cblxuICAgIGlmIChwcm9ncmVzc0Jhcikge1xuICAgICAgcHJvZ3Jlc3NCYXIudXBkYXRlUHJvZ3Jlc3NCYXIoaW5kZXgpO1xuICAgIH1cbiAgICBlbHNlIGlmIChwcm9ncmVzc1RleHQpIHtcbiAgICAgIHVwZGF0ZVByb2dyZXNzVGV4dChcbiAgICAgICAgcHJvZ3Jlc3NUZXh0LFxuICAgICAgICBwYXJhbXMudGV4dHMudGV4dHVhbFByb2dyZXNzLFxuICAgICAgICBpbmRleCxcbiAgICAgICAgcGFyYW1zLm5hdmlnYXRpb25MZW5ndGgsXG4gICAgICAgIHBhcmFtcy50ZXh0cyxcbiAgICAgICk7XG4gICAgfVxuICAgIGVsc2UgaWYgKGRvdHNOYXZpZ2F0aW9uKSB7XG4gICAgICBkb3RzTmF2aWdhdGlvbi50b2dnbGVDdXJyZW50RG90KGluZGV4KTtcbiAgICB9XG5cbiAgICBjYWxjdWxhdGVCdXR0b25WaXNpYmlsaXR5KCk7XG4gIH07XG5cbiAgY29uc3QgcHJldmlvdXMgPSAoKSA9PiB7XG4gICAgc2V0Q3VycmVudEluZGV4KGluZGV4IC0gMSk7XG4gIH07XG5cbiAgY29uc3QgbmV4dCA9ICgpID0+IHtcbiAgICBzZXRDdXJyZW50SW5kZXgoaW5kZXggKyAxKTtcbiAgfTtcblxuICBjb25zdCBzZXROYXZpZ2F0aW9uTGVuZ3RoID0gKG5hdmlnYXRpb25MZW5ndGgpID0+IHtcbiAgICBpZiAodHlwZW9mIG5hdmlnYXRpb25MZW5ndGggIT09ICdudW1iZXInIHx8IG5hdmlnYXRpb25MZW5ndGggPCAwKSB7XG4gICAgICB0aHJvdyBuZXcgRXJyb3IoJ0ludmFsaWQgbmF2aWdhdGlvbiBsZW5ndGgnKTtcbiAgICB9XG5cbiAgICBwYXJhbXMubmF2aWdhdGlvbkxlbmd0aCA9IG5hdmlnYXRpb25MZW5ndGg7XG4gIH07XG5cbiAgY29udGFpbmVyLnNldEN1cnJlbnRJbmRleCA9IHNldEN1cnJlbnRJbmRleDtcbiAgY29udGFpbmVyLnNldE5hdmlnYXRpb25MZW5ndGggPSBzZXROYXZpZ2F0aW9uTGVuZ3RoO1xuICBjb250YWluZXIucHJldmlvdXMgPSBwcmV2aW91cztcbiAgY29udGFpbmVyLm5leHQgPSBuZXh0O1xuICBjb250YWluZXIuc2V0Q2FuU2hvd0xhc3QgPSBzZXRDYW5TaG93TGFzdDtcbiAgY29udGFpbmVyLnByb2dyZXNzQmFyID0gcHJvZ3Jlc3NCYXI7XG4gIGNvbnRhaW5lci5wcm9ncmVzc0RvdHMgPSBkb3RzTmF2aWdhdGlvbjtcblxuICByZXR1cm4gY29udGFpbmVyO1xufVxuXG5leHBvcnQgZGVmYXVsdCBOYXZpZ2F0aW9uO1xuIiwiaW1wb3J0ICcuLi9zdHlsZXMvaDVwLXBsYWNlaG9sZGVyLWltZy5jc3MnO1xuaW1wb3J0IHsgY3JlYXRlRWxlbWVudCB9IGZyb20gJy4uL3V0aWxzLmpzJztcblxuLyoqXG4gKiBSZXR1cm5zIHRydWUgaWYgdGhlIHN0cmluZyBwYXJzZXMgYW5kIGNvbnRhaW5zIGF0IGxlYXN0IG9uZSB2YWxpZCA8c3ZnPiBlbGVtZW50XG4gKiBAcGFyYW0ge3N0cmluZ30gdmFsdWVcbiAqL1xuZnVuY3Rpb24gY29udGFpbnNTdmdFbGVtZW50KHZhbHVlKSB7XG4gIGlmICh0eXBlb2YgdmFsdWUgIT09ICdzdHJpbmcnKSB7XG4gICAgcmV0dXJuIGZhbHNlO1xuICB9XG5cbiAgY29uc3QgaW5wdXQgPSB2YWx1ZS50cmltKCk7XG5cbiAgaWYgKCFpbnB1dC5pbmNsdWRlcygnPHN2ZycpKSB7XG4gICAgcmV0dXJuIGZhbHNlO1xuICB9XG5cbiAgY29uc3QgeG1sRG9jID0gbmV3IERPTVBhcnNlcigpLnBhcnNlRnJvbVN0cmluZyhpbnB1dCwgJ2ltYWdlL3N2Zyt4bWwnKTtcbiAgY29uc3QgaGFzUGFyc2VyRXJyb3IgPSB4bWxEb2MuZ2V0RWxlbWVudHNCeVRhZ05hbWUoJ3BhcnNlcmVycm9yJykubGVuZ3RoID4gMDtcblxuICBpZiAoaGFzUGFyc2VyRXJyb3IpIHtcbiAgICByZXR1cm4gZmFsc2U7XG4gIH1cblxuICByZXR1cm4geG1sRG9jLmdldEVsZW1lbnRzQnlUYWdOYW1lKCdzdmcnKS5sZW5ndGggPiAwO1xufVxuXG4vKipcbiAqICBDcmVhdGUgYSB0aGVtZWQgcGxhY2Vob2xkZXIgc3ZnXG4gKlxuICogIFRoZSBmdW5jdGlvbiBhY2NlcHRzIGVpdGhlcjpcbiAqICAtIEEgc3RyaW5nIGNvbnRhaW5pbmcgYW4gPHN2Zz4gZWxlbWVudCAocmF3IFNWRyBvciBYTUwgdGhhdCBpbmNsdWRlcyBTVkcpXG4gKiAgLSBBIGtleSB0aGF0IG1hdGNoZXMgb25lIG9mIHRoZSBwcmVkZWZpbmVkIHBsYWNlaG9sZGVyIFNWR3MgaW4gJ3BsYWNlaG9sZGVyU1ZHcydcbiAqICAtIElmIG5vIHZhbGlkIFNWRyBvciBrZXkgaXMgcHJvdmlkZWQsIHRoZSAnZGVmYXVsdCcgcGxhY2Vob2xkZXIgaXMgdXNlZC5cbiAqXG4gKiBAcGFyYW0ge3N0cmluZ30gW2FyZ11cbiAqIEEgc3RyaW5nIGNvbnRhaW5pbmcgYW4gPHN2Zz4gZWxlbWVudCBvciBhIGtleSByZWZlcnJpbmcgdG8gYW4gZW50cnkgaW4gJ3BsYWNlaG9sZGVyU1ZHcydcbiAqIEByZXR1cm5zIHtIVE1MRWxlbWVudH0gVGhlIHBsYWNlaG9sZGVyIGltYWdlIGVsZW1lbnRcbiAqL1xuZnVuY3Rpb24gUGxhY2Vob2xkZXJJbWcoYXJnKSB7XG4gIGNvbnN0IHN2ZyA9IGNvbnRhaW5zU3ZnRWxlbWVudChhcmcpXG4gICAgPyBhcmdcbiAgICA6IHBsYWNlaG9sZGVyU1ZHc1thcmddID8/IHBsYWNlaG9sZGVyU1ZHcy5kZWZhdWx0O1xuXG4gIHJldHVybiBjcmVhdGVFbGVtZW50KCdkaXYnLCB7XG4gICAgY2xhc3NMaXN0OiAnaDVwLXRoZW1lLXBsYWNlaG9sZGVyLWltZycsXG4gICAgaW5uZXJIVE1MOiBzdmcsXG4gIH0pO1xufVxuXG4vLyBDYW4ndCB1c2UgaW1nLCBvciBvYmplY3Qgd2l0aCBhIHBhdGggc2luY2Ugd2UgbmVlZCB0byBhY2Nlc3MgdmFyaWFibGVzIG91dHNpZGUgdGhlIHN2Z1xuY29uc3QgcGxhY2Vob2xkZXJTVkdzID0ge1xuICBkZWZhdWx0OiBgXG4gICAgPHN2ZyB2ZXJzaW9uPVwiMS4xXCIgeG1sbnM9XCJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2Z1wiIFxuICAgICAgICB4bWxuczp4bGluaz1cImh0dHA6Ly93d3cudzMub3JnLzE5OTkveGxpbmtcIiB4PVwiMHB4XCIgeT1cIjBweFwiIFxuICAgICAgICB2aWV3Qm94PVwiMCAwIDUwMCA1MDBcIiBzdHlsZT1cImVuYWJsZS1iYWNrZ3JvdW5kOm5ldyAwIDAgNTAwIDUwMDtcIiB4bWw6c3BhY2U9XCJwcmVzZXJ2ZVwiPlxuICAgICAgPHN0eWxlIHR5cGU9XCJ0ZXh0L2Nzc1wiPlxuICAgICAgICAuc3Qwe2ZpbGw6dmFyKC0taDVwLXRoZW1lLWFsdGVybmF0aXZlLWRhcmtlcik7fVxuICAgICAgICAuc3Qxe2ZpbGw6dmFyKC0taDVwLXRoZW1lLWFsdGVybmF0aXZlLWJhc2UpO31cbiAgICAgICAgLnN0MntmaWxsOnZhcigtLWg1cC10aGVtZS1hbHRlcm5hdGl2ZS1kYXJrKTt9XG4gICAgICAgIC5zdDN7ZmlsbDp2YXIoLS1oNXAtdGhlbWUtdWktYmFzZSk7fVxuICAgICAgPC9zdHlsZT5cbiAgICAgIDxnPlxuICAgICAgICA8cGF0aCBjbGFzcz1cInN0MFwiIGQ9XCJNMzY5LjMsMzg4LjljLTAuNSwwLjItMSwwLjMtMS41LDAuNGwtMjU3LjgsMzZjLTIuMywwLjMtNC43LTAuMy02LjYtMS43Yy0xLjktMS40LTMuMS0zLjUtMy40LTUuOEw2NCwxNTkuOWMtMC43LTQuOCwyLjctOS4zLDcuNS0xMGwyNTcuOC0zNmMyLjMtMC4zLDQuNywwLjMsNi42LDEuN2MxLjksMS40LDMuMSwzLjUsMy40LDUuOGwzNiwyNTcuOEMzNzUuOSwzODMuNSwzNzMuMywzODcuNiwzNjkuMywzODguOXpcIi8+XG4gICAgICAgIDxyZWN0IHg9XCIxMTMuOFwiIHk9XCIxMDNcIiB0cmFuc2Zvcm09XCJtYXRyaXgoMC4xMzM3IC0wLjk5MSAwLjk5MSAwLjEzMzcgLTIxLjg1MTcgNDc1LjAwMTMpXCIgY2xhc3M9XCJzdDFcIiB3aWR0aD1cIjI5NFwiIGhlaWdodD1cIjI5NFwiLz5cbiAgICAgICAgPHBvbHlnb24gY2xhc3M9XCJzdDJcIiBwb2ludHM9XCIyNDQuMSwzOTYuMSAyNTIuMSwzMzcuMSAxODEuMywyNzkuMyAxMDIuOSwzMjAuNSA5NS40LDM3NlwiLz5cbiAgICAgICAgPHBvbHlnb24gY2xhc3M9XCJzdDBcIiBwb2ludHM9XCIxMDAuNCwzMzguOSAxOTMuNCwyODkuOSAxODEuNiwyNzkuMSAxMDMsMzE5LjhcIi8+XG4gICAgICAgIDxwYXRoIGNsYXNzPVwic3QwXCIgZD1cIk0xNzIsODkuN2MxMiw0Ny40LDUxLjYsODUuMSwxMDMuMSw5Mi4xYzUxLjQsNi45LDk5LjctMTguOSwxMjMuOC02MS40TDE3Miw4OS43elwiLz5cbiAgICAgICAgPGc+XG4gICAgICAgICAgPGc+XG4gICAgICAgICAgICA8cGF0aCBjbGFzcz1cInN0MlwiIGQ9XCJNMzAwLjksMTA3LjFsLTg4LjMsNDdjMTcuMiwxNC40LDM4LjYsMjQuMyw2Mi42LDI3LjVjNTEuNCw2LjksOTkuNi0xOC44LDEyMy43LTYxLjRMMzAwLjksMTA3LjF6XCIvPlxuICAgICAgICAgIDwvZz5cbiAgICAgICAgPC9nPlxuICAgICAgICA8cG9seWdvbiBjbGFzcz1cInN0MlwiIHBvaW50cz1cIjQwMS4xLDMwOSAzNTEuNiwyNjguNSAxMzYuOSwzODEuNiAzODYuOCw0MTUuM1wiLz5cbiAgICAgICAgPHBvbHlnb24gY2xhc3M9XCJzdDBcIiBwb2ludHM9XCIxNzAuOSwzODYuMiAzNjcuNCwyODIuNCAzNTEuOSwyNjguMyAxMzQuMSwzODEuMlwiLz5cbiAgICAgICAgPHBhdGggY2xhc3M9XCJzdDNcIiBkPVwiTTM4Ny4zLDQyNS4zYy0wLjYsMC0xLjIsMC0xLjgtMC4xTDk0LjEsMzg1LjljLTIuNi0wLjQtNS0xLjctNi42LTMuOGMtMS42LTIuMS0yLjMtNC44LTItNy40bDM5LjMtMjkxLjRjMC43LTUuNSw1LjgtOS4zLDExLjItOC42bDI5MS40LDM5LjNjMi42LDAuNCw1LDEuNyw2LjYsMy44YzEuNiwyLjEsMi4zLDQuOCwyLDcuNGwtMzkuMywyOTEuNEMzOTYsNDIxLjUsMzkyLDQyNS4xLDM4Ny4zLDQyNS4zek0xMDYuNywzNjcuNWwyNzEuNSwzNi42bDM2LjYtMjcxLjVMMTQzLjMsOTUuOUwxMDYuNywzNjcuNXpcIi8+XG4gICAgICA8L2c+XG4gICAgPC9zdmc+XG4gICAgYCxcbiAgaDVwSW1hZ2VEZWZhdWx0OiBgXG4gICAgPHN2ZyBjbGFzcz1cImg1cC1pbWFnZS1wbGFjZWhvbGRlci1zdmdcIiB4bWxucz1cImh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnXCIgdmVyc2lvbj1cIjEuMVwiIHZpZXdCb3g9XCIwIDAgOTAzIDQ1OVwiIHByZXNlcnZlQXNwZWN0UmF0aW89XCJ4TWlkWU1pZCBzbGljZVwiPlxuICAgICAgPGRlZnM+XG4gICAgICAgIDxzdHlsZT5cbiAgICAgICAgICAuY2xzLTEge2ZpbGw6IHZhcigtLWg1cC10aGVtZS1hbHRlcm5hdGl2ZS1kYXJrZXIpO31cbiAgICAgICAgICAuY2xzLTIge2ZpbGw6IHZhcigtLWg1cC10aGVtZS1hbHRlcm5hdGl2ZS1kYXJrKTt9XG4gICAgICAgICAgLmNscy0zIHtmaWxsOiB2YXIoLS1oNXAtdGhlbWUtYWx0ZXJuYXRpdmUtYmFzZSk7fVxuICAgICAgICA8L3N0eWxlPlxuICAgICAgPC9kZWZzPlxuICAgICAgPGc+XG4gICAgICAgIDxnPlxuICAgICAgICAgIDxyZWN0IGNsYXNzPVwiY2xzLTNcIiB4PVwiMVwiIHk9XCIwXCIgd2lkdGg9XCI5MDMuMVwiIGhlaWdodD1cIjQ1OS4xXCIvPlxuICAgICAgICAgIDxwb2x5Z29uIGNsYXNzPVwiY2xzLTJcIiBwb2ludHM9XCI1MjcuNSA0NTkuNSA1MjcuNSAzMzQuMSAzNjQuOCAyMzQgNDguMSA0NTkuNSA1MjcuNSA0NTkuNVwiLz5cbiAgICAgICAgICA8cG9seWdvbiBjbGFzcz1cImNscy0yXCIgcG9pbnRzPVwiOTA0LjIgMjQ2IDczMi4yIDE0Mi42IDI4Ny4xIDQ1OS44IDkwNC4yIDQ1OS44IDkwNC4yIDI0NlwiLz5cbiAgICAgICAgICA8cG9seWdvbiBjbGFzcz1cImNscy0yXCIgcG9pbnRzPVwiMzk0LjcgNDU5LjUgMTA2LjMgMjU0IC4xIDMzMi40IC4xIDQ1OS41IDM5NC43IDQ1OS41XCIvPlxuICAgICAgICAgIDxwb2x5Z29uIGNsYXNzPVwiY2xzLTFcIiBwb2ludHM9XCItLjMgMzY2LjkgMTMzLjggMjc0LjIgMTA1LjEgMjU1LjcgLS4zIDMzMi45IC0uMyAzNjYuOVwiLz5cbiAgICAgICAgICA8cG9seWdvbiBjbGFzcz1cImNscy0xXCIgcG9pbnRzPVwiMzcwLjUgNDU5LjIgNzcxLjYgMTY4LjcgNzMyLjIgMTQyLjYgMjkyIDQ1OS4yIDM3MC41IDQ1OS4yXCIvPlxuICAgICAgICAgIDxwb2x5Z29uIGNsYXNzPVwiY2xzLTFcIiBwb2ludHM9XCIxMDIuOCA0NTkuNSAzOTIuOCAyNTIuNiAzNjUuMyAyMzMuNSA0My42IDQ1OS41IDEwMi44IDQ1OS41XCIvPlxuICAgICAgICAgIDxwYXRoIGNsYXNzPVwiY2xzLTFcIiBkPVwiTTQzLjMuNGMzMC4xLDc4LDEwNS43LDEzMy4zLDE5NC4zLDEzMy4zUzQwMS44LDc4LjMsNDMxLjguNEg0My4zWlwiLz5cbiAgICAgICAgICA8cGF0aCBjbGFzcz1cImNscy0yXCIgZD1cIk0yNjcuNC40TDEyNi43LDEwMS42YzMyLjEsMjAuMyw3MC4xLDMyLDExMC45LDMyLDg4LjYsMCwxNjQuMi01NS4zLDE5NC4zLTEzMy4zaC0xNjQuNVpcIi8+XG4gICAgICAgIDwvZz5cbiAgICAgIDwvZz5cbiAgICA8L3N2Zz5cbiAgICBgLFxufTtcblxuZXhwb3J0IGRlZmF1bHQgUGxhY2Vob2xkZXJJbWc7XG4iLCJpbXBvcnQgJy4uL3N0eWxlcy9oNXAtcmVzdWx0LXNjcmVlbi5jc3MnO1xuaW1wb3J0IHsgY3JlYXRlRWxlbWVudCB9IGZyb20gJy4uL3V0aWxzLmpzJztcbi8qKlxuICogQHR5cGVkZWYgUmVzdWx0UXVlc3Rpb25cbiAqIEB0eXBlIHtvYmplY3R9XG4gKiBAcHJvcGVydHkge1tzdHJpbmddfSBpbWdVcmwgVGhlIHVybCB0byBhbiBpbWFnZSB0byBkaXNwbGF5IGJlZm9yZSB0aGUgcXVlc3Rpb25cbiAqIEBwcm9wZXJ0eSB7W2Jvb2xlYW5dfSB1c2VEZWZhdWx0SW1nIFVzZSBhIGRlZmF1bHQgaW1hZ2UuIFdpbGwgYmUgb3ZlcndyaXR0ZW4gYnkgaW1nVXJsXG4gKiBAcHJvcGVydHkge3N0cmluZ30gdGl0bGUgVGhlIHRleHR1YWwgZGVzY3JpcHRpb24gb2YgdGhlIHF1ZXN0aW9uXG4gKiBAcHJvcGVydHkge3N0cmluZ30gcG9pbnRzIFRoZSBzY29yZSBvZiB0aGUgcXVlc3Rpb25cbiAqIEBwcm9wZXJ0eSB7W2Jvb2xlYW5dfSBpc0NvcnJlY3QgSWYgdGhlIGFuc3dlciBpcyBjb3JyZWN0IChTb21lIGNvbnRlbnQgdHlwZXMgYXJlIG1vcmUgbGVuaWVudClcbiAqIEBwcm9wZXJ0eSB7W3N0cmluZ119IHVzZXJBbnN3ZXIgV2hhdCB0aGUgdXNlciBhbnN3ZXJlZFxuICogQHByb3BlcnR5IHtbc3RyaW5nXX0gY29ycmVjdEFuc3dlciBUaGUgY29ycmVjdCBhbnN3ZXJcbiAqIEBwcm9wZXJ0eSB7W3N0cmluZ119IGNvcnJlY3RBbnN3ZXJQcmVwZW5kIFRoZSBsYWJlbCBiZWZvcmUgdGhlIGNvcnJlY3QgYW5zd2VyXG4gKi9cblxuLyoqXG4gKiBAdHlwZWRlZiBSZXN1bHRRdWVzdGlvbkdyb3VwXG4gKiBAdHlwZSB7b2JqZWN0fVxuICogQHByb3BlcnR5IHtbc3RyaW5nW11dfSBsaXN0SGVhZGVycyBUaGUgdGFibGUgaGVhZGVyc1xuICogQHByb3BlcnR5IHtSZXN1bHRRdWVzdGlvbltdfSBxdWVzdGlvbnMgVGhlIGxpc3Qgb2YgdGFza3MgdG8gYmUgc3VtbWFyaXplZFxuICovXG5cbi8qKlxuICogQHR5cGVkZWYgUmVzdWx0U2NyZWVuUGFyYW1zXG4gKiBAdHlwZSB7b2JqZWN0fVxuICogQHByb3BlcnR5IHtzdHJpbmd9IGhlYWRlciBUaGUgbWFpbiBoZWFkZXIgb2YgdGhlIHJlc3VsdCBzY3JlZW5cbiAqIEBwcm9wZXJ0eSB7c3RyaW5nfSBzY29yZUhlYWRlciBUaGUgaGVhZGVyIGRldGFpbGluZyB0aGUgdG90YWwgc2NvcmVcbiAqIEBwcm9wZXJ0eSB7UmVzdWx0UXVlc3Rpb25Hcm91cFtdfSBxdWVzdGlvbkdyb3VwcyBUaGUgZ3JvdXBzIG9mIHF1ZXN0aW9uc1xuICovXG5cbi8qKlxuICogQ3JlYXRlIGEgcmVzdWx0IHNjcmVlbiwgc3VtbWluZyB1cCB0aGUgdGFza3Mgb2YgdGhlIGNvbnRlbnQgYW5kIHRoZSBzY29yZXMgYWNoaWV2ZWRcbiAqIEBwYXJhbSB7UmVzdWx0U2NyZWVuUGFyYW1zfSBwYXJhbXMgQSBzZXQgb2YgcGFyYW1ldGVycyB0byBjb25maWd1cmUgdGhlIFJlc3VsdFNjcmVlbiBjb21wb25lbnRcbiAqIEByZXR1cm5zIHtIVE1MRWxlbWVudH0gVGhlIHJlc3VsdCBzY3JlZW4gZWxlbWVudFxuICovXG5mdW5jdGlvbiBSZXN1bHRTY3JlZW4ocGFyYW1zKSB7XG4gIC8vIENyZWF0ZSBtYWluIHdyYXBwZXJcbiAgY29uc3QgcmVzdWx0U2NyZWVuID0gY3JlYXRlRWxlbWVudCgnZGl2JywgeyBjbGFzc0xpc3Q6ICdoNXAtdGhlbWUtcmVzdWx0LXNjcmVlbicgfSk7XG5cbiAgLy8gQ3JlYXRlIGhlYWRlciBiYW5uZXJcbiAgY29uc3QgaGVhZGVyID0gY3JlYXRlRWxlbWVudCgnZGl2JywgeyBjbGFzc0xpc3Q6ICdoNXAtdGhlbWUtcmVzdWx0cy1iYW5uZXInIH0pO1xuICBoZWFkZXIuYXBwZW5kQ2hpbGQoY3JlYXRlRWxlbWVudCgnZGl2JywgeyBjbGFzc0xpc3Q6ICdoNXAtdGhlbWUtcGF0dGVybicgfSkpO1xuICBoZWFkZXIuYXBwZW5kQ2hpbGQoY3JlYXRlRWxlbWVudCgnZGl2Jywge1xuICAgIGNsYXNzTGlzdDogJ2g1cC10aGVtZS1yZXN1bHRzLXRpdGxlJyxcbiAgICB0ZXh0Q29udGVudDogcGFyYW1zLmhlYWRlcixcbiAgfSkpO1xuICBoZWFkZXIuYXBwZW5kQ2hpbGQoY3JlYXRlRWxlbWVudCgnZGl2Jywge1xuICAgIGNsYXNzTGlzdDogJ2g1cC10aGVtZS1yZXN1bHRzLXNjb3JlJyxcbiAgICBpbm5lckhUTUw6IHBhcmFtcy5zY29yZUhlYWRlcixcbiAgfSkpO1xuICByZXN1bHRTY3JlZW4uYXBwZW5kKGhlYWRlcik7XG5cbiAgLy8gQ3JlYXRlIHRoZSBzdW1tYXJ5IHRhYmxlXG4gIHBhcmFtcy5xdWVzdGlvbkdyb3Vwcy5mb3JFYWNoKChncm91cCkgPT4ge1xuICAgIGNvbnN0IGdyb3VwQ29udGFpbmVyID0gY3JlYXRlRWxlbWVudCgnZGl2Jywge1xuICAgICAgY2xhc3NMaXN0OiAnaDVwLXRoZW1lLXJlc3VsdHMtbGlzdC1jb250YWluZXInLFxuICAgIH0pO1xuXG4gICAgaWYgKGdyb3VwLmxpc3RIZWFkZXJzKSB7XG4gICAgICBjb25zdCBsaXN0SGVhZGVycyA9IGNyZWF0ZUVsZW1lbnQoJ2RpdicsIHsgY2xhc3NMaXN0OiAnaDVwLXRoZW1lLXJlc3VsdHMtbGlzdC1oZWFkaW5nJyB9KTtcbiAgICAgIGdyb3VwLmxpc3RIZWFkZXJzLmZvckVhY2goKHRpdGxlKSA9PiB7XG4gICAgICAgIGxpc3RIZWFkZXJzLmFwcGVuZENoaWxkKGNyZWF0ZUVsZW1lbnQoJ2RpdicsIHsgY2xhc3NMaXN0OiAnaGVhZGluZy1pdGVtJywgdGV4dENvbnRlbnQ6IHRpdGxlIH0pKTtcbiAgICAgIH0pO1xuICAgICAgZ3JvdXBDb250YWluZXIuYXBwZW5kQ2hpbGQobGlzdEhlYWRlcnMpO1xuICAgIH1cblxuICAgIGNvbnN0IHJlc3VsdExpc3QgPSBjcmVhdGVFbGVtZW50KCd1bCcsIHsgY2xhc3NMaXN0OiAnaDVwLXRoZW1lLXJlc3VsdHMtbGlzdCcgfSk7XG5cbiAgICBncm91cC5xdWVzdGlvbnMuZm9yRWFjaCgocXVlc3Rpb24pID0+IHtcbiAgICAgIHJlc3VsdExpc3QuYXBwZW5kQ2hpbGQoY3JlYXRlUXVlc3Rpb24ocXVlc3Rpb24pKTtcbiAgICB9KTtcblxuICAgIGdyb3VwQ29udGFpbmVyLmFwcGVuZENoaWxkKHJlc3VsdExpc3QpO1xuICAgIHJlc3VsdFNjcmVlbi5hcHBlbmRDaGlsZChncm91cENvbnRhaW5lcik7XG4gIH0pO1xuXG4gIHJldHVybiByZXN1bHRTY3JlZW47XG59XG5cbmNvbnN0IGNyZWF0ZVF1ZXN0aW9uID0gKHF1ZXN0aW9uKSA9PiB7XG4gIGNvbnN0IGxpc3RJdGVtID0gY3JlYXRlRWxlbWVudCgnbGknLCB7XG4gICAgY2xhc3NMaXN0OiAnaDVwLXRoZW1lLXJlc3VsdHMtbGlzdC1pdGVtJyxcbiAgfSk7XG5cbiAgaWYgKHF1ZXN0aW9uLmltZ1VybCkge1xuICAgIGxpc3RJdGVtLmFwcGVuZENoaWxkKGNyZWF0ZUVsZW1lbnQoXG4gICAgICAnZGl2JyxcbiAgICAgIHsgY2xhc3NMaXN0OiAnaDVwLXRoZW1lLXJlc3VsdHMtaW1hZ2UnIH0sXG4gICAgICB7ICdiYWNrZ3JvdW5kLWltYWdlJzogYHVybChcIiR7cXVlc3Rpb24uaW1nVXJsfVwiKWAgfSxcbiAgICApKTtcbiAgfVxuICBlbHNlIGlmIChxdWVzdGlvbi51c2VEZWZhdWx0SW1nKSB7XG4gICAgY29uc3QgaW1hZ2VDb250YWluZXIgPSBjcmVhdGVFbGVtZW50KCdkaXYnLCB7XG4gICAgICBjbGFzc0xpc3Q6ICdoNXAtdGhlbWUtcmVzdWx0cy1pbWFnZScsXG4gICAgfSk7XG5cbiAgICBpbWFnZUNvbnRhaW5lci5hcHBlbmRDaGlsZChINVAuQ29tcG9uZW50cy5QbGFjZWhvbGRlckltZygnaDVwSW1hZ2VEZWZhdWx0JykpO1xuXG4gICAgbGlzdEl0ZW0uYXBwZW5kQ2hpbGQoaW1hZ2VDb250YWluZXIpO1xuICB9XG5cbiAgY29uc3QgcXVlc3Rpb25Db250YWluZXIgPSBjcmVhdGVFbGVtZW50KCdkaXYnLCB7XG4gICAgY2xhc3NMaXN0OiAnaDVwLXRoZW1lLXJlc3VsdHMtcXVlc3Rpb24tY29udGFpbmVyJyxcbiAgfSk7XG5cbiAgcXVlc3Rpb25Db250YWluZXIuYXBwZW5kQ2hpbGQoY3JlYXRlRWxlbWVudCgnZGl2Jywge1xuICAgIGNsYXNzTGlzdDogJ2g1cC10aGVtZS1yZXN1bHRzLXF1ZXN0aW9uJyxcbiAgICBpbm5lckhUTUw6IHF1ZXN0aW9uLnRpdGxlLFxuICB9KSk7XG5cbiAgLy8gVXNlckFuc3dlciBtaWdodCBiZSBhbiBlbXB0eSBzdHJpbmdcbiAgaWYgKHR5cGVvZiAocXVlc3Rpb24udXNlckFuc3dlcikgPT09ICdzdHJpbmcnKSB7XG4gICAgY29uc3QgYW5zd2VyQ29udGFpbmVyID0gY3JlYXRlRWxlbWVudCgnZGl2Jywge1xuICAgICAgY2xhc3NMaXN0OiAnaDVwLXRoZW1lLXJlc3VsdHMtYW5zd2VyJyxcbiAgICB9KTtcblxuICAgIGNvbnN0IGFuc3dlciA9IGNyZWF0ZUVsZW1lbnQoJ3NwYW4nLCB7XG4gICAgICBjbGFzc0xpc3Q6ICdoNXAtdGhlbWUtcmVzdWx0cy1ib3gtc21hbGwgaDVwLXRoZW1lLXJlc3VsdHMtY29ycmVjdCcsXG4gICAgICB0ZXh0Q29udGVudDogcXVlc3Rpb24udXNlckFuc3dlcixcbiAgICB9KTtcbiAgICBhbnN3ZXJDb250YWluZXIuYXBwZW5kQ2hpbGQoYW5zd2VyKTtcblxuICAgIC8vIGlzQ29ycmVjdCBkZWZpbmVkIEFORCBmYWxzZVxuICAgIGlmIChxdWVzdGlvbi5pc0NvcnJlY3QgPT09IGZhbHNlKSB7XG4gICAgICBhbnN3ZXIuY2xhc3NMaXN0LmFkZCgnaDVwLXRoZW1lLXJlc3VsdHMtaW5jb3JyZWN0Jyk7XG4gICAgICBhbnN3ZXIuY2xhc3NMaXN0LnJlbW92ZSgnaDVwLXRoZW1lLXJlc3VsdHMtY29ycmVjdCcpO1xuXG4gICAgICBpZiAocXVlc3Rpb24uY29ycmVjdEFuc3dlcikge1xuICAgICAgICBjb25zdCBzb2x1dGlvbkNvbnRhaW5lciA9IGNyZWF0ZUVsZW1lbnQoJ3NwYW4nLCB7XG4gICAgICAgICAgY2xhc3NMaXN0OiAnaDVwLXRoZW1lLXJlc3VsdHMtc29sdXRpb24nLFxuICAgICAgICB9KTtcblxuICAgICAgICBpZiAocXVlc3Rpb24uY29ycmVjdEFuc3dlclByZXBlbmQpIHtcbiAgICAgICAgICBzb2x1dGlvbkNvbnRhaW5lci5hcHBlbmRDaGlsZChjcmVhdGVFbGVtZW50KCdzcGFuJywge1xuICAgICAgICAgICAgY2xhc3NMaXN0OiAnaDVwLXRoZW1lLXJlc3VsdHMtc29sdXRpb24tbGFiZWwnLFxuICAgICAgICAgICAgdGV4dENvbnRlbnQ6IHF1ZXN0aW9uLmNvcnJlY3RBbnN3ZXJQcmVwZW5kLFxuICAgICAgICAgIH0pKTtcbiAgICAgICAgfVxuXG4gICAgICAgIHNvbHV0aW9uQ29udGFpbmVyLmlubmVySFRNTCArPSBxdWVzdGlvbi5jb3JyZWN0QW5zd2VyO1xuXG4gICAgICAgIGFuc3dlckNvbnRhaW5lci5hcHBlbmRDaGlsZChzb2x1dGlvbkNvbnRhaW5lcik7XG4gICAgICB9XG4gICAgfVxuXG4gICAgcXVlc3Rpb25Db250YWluZXIuYXBwZW5kQ2hpbGQoYW5zd2VyQ29udGFpbmVyKTtcbiAgfVxuXG4gIGxpc3RJdGVtLmFwcGVuZENoaWxkKHF1ZXN0aW9uQ29udGFpbmVyKTtcblxuICBsaXN0SXRlbS5hcHBlbmRDaGlsZChjcmVhdGVFbGVtZW50KCdkaXYnLCB7XG4gICAgY2xhc3NMaXN0OiAnaDVwLXRoZW1lLXJlc3VsdHMtcG9pbnRzJyxcbiAgICBpbm5lckhUTUw6IHF1ZXN0aW9uLnBvaW50cyxcbiAgfSkpO1xuXG4gIHJldHVybiBsaXN0SXRlbTtcbn07XG5cbmV4cG9ydCBkZWZhdWx0IFJlc3VsdFNjcmVlbjtcbiIsImltcG9ydCAnLi4vc3R5bGVzL2g1cC1jb21wb25lbnRzLmNzcyc7XG5pbXBvcnQgQ292ZXJQYWdlIGZyb20gJy4uL2NvbXBvbmVudHMvaDVwLWNvdmVyLXBhZ2UuanMnO1xuaW1wb3J0IEJ1dHRvbiBmcm9tICcuLi9jb21wb25lbnRzL2g1cC1idXR0b24uanMnO1xuaW1wb3J0IERyYWdnYWJsZSBmcm9tICcuLi9jb21wb25lbnRzL2g1cC1kcmFnZ2FibGUuanMnO1xuaW1wb3J0IERyb3B6b25lIGZyb20gJy4uL2NvbXBvbmVudHMvaDVwLWRyb3B6b25lLmpzJztcbmltcG9ydCBOYXZpZ2F0aW9uIGZyb20gJy4uL2NvbXBvbmVudHMvaDVwLW5hdmlnYXRpb24uanMnO1xuaW1wb3J0IFBsYWNlaG9sZGVySW1nIGZyb20gJy4uL2NvbXBvbmVudHMvaDVwLXBsYWNlaG9sZGVyLWltZy5qcyc7XG5pbXBvcnQgUHJvZ3Jlc3NCYXIgZnJvbSAnLi4vY29tcG9uZW50cy9oNXAtcHJvZ3Jlc3MtYmFyLmpzJztcbmltcG9ydCBQcm9ncmVzc0RvdHMgZnJvbSAnLi4vY29tcG9uZW50cy9oNXAtcHJvZ3Jlc3MtZG90cy5qcyc7XG5pbXBvcnQgUmVzdWx0U2NyZWVuIGZyb20gJy4uL2NvbXBvbmVudHMvaDVwLXJlc3VsdC1zY3JlZW4uanMnO1xuXG4vLyBlc2xpbnQtZGlzYWJsZS1uZXh0LWxpbmUgbm8tZ2xvYmFsLWFzc2lnblxuSDVQID0gSDVQIHx8IHt9O1xuSDVQLkNvbXBvbmVudHMgPSBINVAuQ29tcG9uZW50cyB8fCB7fTtcblxuSDVQLkNvbXBvbmVudHMuQ292ZXJQYWdlID0gQ292ZXJQYWdlO1xuSDVQLkNvbXBvbmVudHMuQnV0dG9uID0gQnV0dG9uO1xuSDVQLkNvbXBvbmVudHMuRHJhZ2dhYmxlID0gRHJhZ2dhYmxlO1xuSDVQLkNvbXBvbmVudHMuRHJvcHpvbmUgPSBEcm9wem9uZTtcbkg1UC5Db21wb25lbnRzLk5hdmlnYXRpb24gPSBOYXZpZ2F0aW9uO1xuSDVQLkNvbXBvbmVudHMuUGxhY2Vob2xkZXJJbWcgPSBQbGFjZWhvbGRlckltZztcbkg1UC5Db21wb25lbnRzLlByb2dyZXNzQmFyID0gUHJvZ3Jlc3NCYXI7XG5INVAuQ29tcG9uZW50cy5Qcm9ncmVzc0RvdHMgPSBQcm9ncmVzc0RvdHM7XG5INVAuQ29tcG9uZW50cy5SZXN1bHRTY3JlZW4gPSBSZXN1bHRTY3JlZW47XG4iXSwibmFtZXMiOlsiREVCT1VOQ0VfREVMQVlfTVMiLCJERUZBVUxUX0xJTkVfSEVJR0hUIiwiQ0xPU0VfVE9fSU5URUdFUl9FUFNJTE9OIiwicGFyc2VTdHJpbmciLCJ0ZXh0IiwidW5kZWZpbmVkIiwiZGl2IiwiZG9jdW1lbnQiLCJjcmVhdGVFbGVtZW50IiwiaW5uZXJIVE1MIiwidGV4dENvbnRlbnQiLCJ0YWciLCJvcHRpb25zIiwic3R5bGUiLCJlbGVtZW50IiwiT2JqZWN0IiwiYXNzaWduIiwiY29tcHV0ZUxpbmVDb3VudCIsImdldENvbXB1dGVkU3R5bGUiLCJsaW5lSGVpZ2h0IiwicGFyc2VGbG9hdCIsImlzTmFOIiwiZm9udFNpemUiLCJlbGVtZW50SGVpZ2h0IiwiZ2V0Qm91bmRpbmdDbGllbnRSZWN0IiwiaGVpZ2h0IiwibnVtYmVyT2ZMaW5lc0V4YWN0IiwiZmxvYXRpbmdWYWx1ZSIsIk1hdGgiLCJhYnMiLCJyb3VuZCIsImlzQ2xvc2VUb0ludGVnZXIiLCJjZWlsIiwiY29tcHV0ZVdpZHRoUmF0aW8iLCJlbGVtZW50QSIsImVsZW1lbnRCIiwid2lkdGhBIiwib2Zmc2V0V2lkdGgiLCJ3aWR0aEIiLCJjbGllbnRXaWR0aCIsImRlYm91bmNlIiwiY2FsbGJhY2siLCJkZWxheU1zIiwidGltZW91dElkIiwiYXJncyIsImNsZWFyVGltZW91dCIsInNldFRpbWVvdXQiLCJVdGlscyIsIk1BWF9MQUJFTF9MSU5FX0NPVU5UIiwiTUFYX0xBQkVMX1dJRFRIX1JBVElPIiwiQnV0dG9uIiwicGFyYW1zIiwiYmFzZUNsYXNzIiwiYnV0dG9uU3R5bGVUeXBlIiwic3R5bGVUeXBlIiwidG9vbHRpcCIsImljb24iLCJsYWJlbCIsImJ1dHRvbiIsImFyaWFMYWJlbCIsImNsYXNzTGlzdCIsImNsYXNzZXMiLCJvbmNsaWNrIiwib25DbGljayIsInR5cGUiLCJidXR0b25UeXBlIiwiZGlzYWJsZWQiLCJINVAiLCJUb29sdGlwIiwicG9zaXRpb24iLCJ0b29sdGlwUG9zaXRpb24iLCJJY29uT25seU9ic2VydmVyIiwib2JzZXJ2ZSIsIlJlc2l6ZU9ic2VydmVyIiwiZW50cmllcyIsImVudHJ5IiwidGFyZ2V0IiwiaXNDb25uZWN0ZWQiLCJtYXRjaGVzIiwicXVlcnlTZWxlY3RvciIsImxpbmVDb3VudCIsInJhdGlvIiwic2hvdWxkSGlkZSIsInBhcmVudCIsInBhcmVudEVsZW1lbnQiLCJjaGlsZCIsImNoaWxkcmVuIiwiSFRNTEJ1dHRvbkVsZW1lbnQiLCJ0b2dnbGUiLCJDb3ZlclBhZ2UiLCJjb3ZlclBhZ2VDbGFzc2VzIiwidXNlTWVkaWFDb250YWluZXIiLCJpbWciLCJjb3ZlclBhZ2UiLCJhcHBlbmRDaGlsZCIsInNyYyIsImFsdCIsImltZ0FsdCIsImRldGFpbENvbnRhaW5lciIsImFyaWFIaWRkZW4iLCJ0aXRsZSIsImRlc2NyaXB0aW9uIiwiYnV0dG9uTGFiZWwiLCJidXR0b25PbkNsaWNrIiwiRHJhZ2dhYmxlIiwiaGFzSGFuZGxlIiwic3RhdHVzQ2hhbmdlc0JhY2tncm91bmQiLCJwb2ludHNBbmRTdGF0dXMiLCJzZXRDb250ZW50IiwiZG9tIiwiZHJhZ2dhYmxlIiwiYXBwZW5kIiwicm9sZSIsInRhYkluZGV4Iiwic2V0QXR0cmlidXRlIiwiYXJpYUdyYWJiZWQiLCJqUXVlcnkiLCJyZXZlcnQiLCJoYW5kbGVSZXZlcnQiLCJkcmFnIiwiaGFuZGxlRHJhZ0V2ZW50Iiwic3RhcnQiLCJoYW5kbGVEcmFnU3RhcnRFdmVudCIsInN0b3AiLCJoYW5kbGVEcmFnU3RvcEV2ZW50IiwiY29udGFpbm1lbnQiLCJzZXRDb250ZW50T3BhY2l0eSIsInZhbHVlIiwic2FuaXRpemVkVmFsdWUiLCJtYXgiLCJtaW4iLCJOdW1iZXIiLCJzZXRQcm9wZXJ0eSIsInNldE9wYWNpdHkiLCJzZXREcmFnSGFuZGxlVmlzaWJpbGl0eSIsImdldEJvcmRlcldpZHRoIiwiY29tcHV0ZWRTdHlsZSIsIndpbmRvdyIsImdldFByb3BlcnR5VmFsdWUiLCJEcm9wem9uZSIsInZhcmlhbnQiLCJjb250YWluZXJDbGFzc2VzIiwicHVzaCIsImJhY2tncm91bmRPcGFjaXR5Iiwiam9pbiIsImFyaWFEaXNhYmxlZCIsImRyb3B6b25lQ29udGFpbmVyIiwiYXJlYUxhYmVsIiwiJGRyb3B6b25lIiwidGFiaW5kZXgiLCJjbGFzcyIsImFwcGVuZFRvIiwiZHJvcHBhYmxlIiwiYWN0aXZlQ2xhc3MiLCJ0b2xlcmFuY2UiLCJhY2NlcHQiLCJoYW5kbGVBY2NlcHRFdmVudCIsIm92ZXIiLCJldmVudCIsInVpIiwiZHJvcHpvbmUiLCJhZGQiLCJoYW5kbGVEcm9wT3ZlckV2ZW50Iiwib3V0IiwicmVtb3ZlIiwiaGFuZGxlRHJvcE91dEV2ZW50IiwiZHJvcCIsImhhbmRsZURyb3BFdmVudCIsImluZGV4IiwiZ2V0IiwiUHJvZ3Jlc3NCYXIiLCJwcm9ncmVzc0xlbmd0aCIsInByb2dyZXNzQmFyIiwiYXJpYVZhbHVlTWF4IiwiYXJpYVZhbHVlTWluIiwiYXJpYVZhbHVlTm93IiwicHJvZ3Jlc3NCYXJJbm5lciIsInVwZGF0ZVByb2dyZXNzQmFyIiwibmV3SW5kZXgiLCJ0b0ZpeGVkIiwid2lkdGgiLCJQcm9ncmVzc0RvdHMiLCJkb3RzIiwibGVuZ3RoIiwiYWN0aXZlSW5kZXgiLCJwcm9ncmVzc0RvdEVsZW1lbnRzIiwiZG90c0NvbnRhaW5lciIsImNsYXNzTmFtZSIsIm9uUHJvZ3Jlc3NEb3RDbGljayIsInByZXZlbnREZWZhdWx0IiwiZ2V0QXR0cmlidXRlIiwidG9nZ2xlQ3VycmVudERvdCIsImhhbmRsZVByb2dyZXNzRG90Q2xpY2siLCJvbktleURvd24iLCJjb2RlIiwic2V0QWN0aXZlRG90IiwiaGFzT25lRm9jdXNhYmxlRG90Iiwic29tZSIsImRvdCIsImZvckVhY2giLCJpIiwiaXRlbSIsInByb2dyZXNzRG90IiwiaHJlZiIsIm9ua2V5ZG93biIsInBsYWNlRm9jdXMiLCJlbCIsImZvY3VzIiwidGV4dHMiLCJpc0N1cnJlbnQiLCJqdW1wVG9RdWVzdGlvbiIsInJlcGxhY2UiLCJ0b1N0cmluZyIsImlzQW5zd2VyZWQiLCJjb250YWlucyIsImFuc3dlcmVkVGV4dCIsInVuYW5zd2VyZWRUZXh0IiwiY3VycmVudFF1ZXN0aW9uVGV4dCIsInRvZ2dsZUZpbGxlZERvdCIsImZpbGxlZEluZGV4IiwiaXNGaWxsZWQiLCJjcmVhdGVFbGVtZW50c0Zyb21QbGFjZWhvbGRlcnMiLCJyZXBsYWNlbWVudHMiLCJwbGFjZWhvbGRlcnMiLCJrZXlzIiwicmVnRXhwIiwiUmVnRXhwIiwibWFwIiwicCIsInNwbGl0IiwiZmlsdGVyIiwicGFydCIsImNyZWF0ZVRleHROb2RlIiwiY3JlYXRlUHJvZ3Jlc3NTcGFuIiwiY29udGVudCIsInRvb2x0aXBUZXh0Iiwic3BhbiIsImlubmVyVGV4dCIsInVwZGF0ZVByb2dyZXNzVGV4dCIsInByb2dyZXNzVGV4dCIsInRleHR1YWxQcm9ncmVzcyIsImN1cnJlbnRJbmRleCIsIm5hdmlnYXRpb25MZW5ndGgiLCJkb21QYXJ0cyIsIkBjdXJyZW50IiwiY3VycmVudFRvb2x0aXAiLCJAdG90YWwiLCJ0b3RhbFRvb2x0aXAiLCJjcmVhdGVQcm9ncmVzc1RleHQiLCJOYXZpZ2F0aW9uIiwiZG90c05hdmlnYXRpb24iLCJwcmV2QnV0dG9uIiwibmV4dEJ1dHRvbiIsImxhc3RCdXR0b24iLCJjYW5TaG93TGFzdCIsImNvbnRhaW5lciIsImhhbmRsZVByZXZpb3VzIiwicHJldkNsYXNzTGlzdCIsInByZXZpb3VzQnV0dG9uIiwicHJldmlvdXNCdXR0b25BcmlhIiwicHJldmlvdXNUb29sdGlwIiwic2hvd0Rpc2FibGVkQnV0dG9ucyIsInByZXZpb3VzIiwicHJvZ3Jlc3NUeXBlIiwicHJvZ3Jlc3NDb250YWluZXIiLCJ0aXRsZXMiLCJwcm9ncmVzc1dyYXBwZXIiLCJoYW5kbGVOZXh0IiwibmV4dENsYXNzTGlzdCIsIm5leHRCdXR0b25BcmlhIiwibmV4dFRvb2x0aXAiLCJuZXh0IiwiaGFuZGxlTGFzdCIsImxhc3RCdXR0b25BcmlhIiwibGFzdFRvb2x0aXAiLCJjYWxjdWxhdGVCdXR0b25WaXNpYmlsaXR5IiwidG9nZ2xlQXR0cmlidXRlIiwiaXNMYXN0UGFnZSIsInNldENhblNob3dMYXN0IiwiY2FuU2hvdyIsInNldEN1cnJlbnRJbmRleCIsInNldE5hdmlnYXRpb25MZW5ndGgiLCJFcnJvciIsInByb2dyZXNzRG90cyIsImNvbnRhaW5zU3ZnRWxlbWVudCIsImlucHV0IiwidHJpbSIsImluY2x1ZGVzIiwieG1sRG9jIiwiRE9NUGFyc2VyIiwicGFyc2VGcm9tU3RyaW5nIiwiaGFzUGFyc2VyRXJyb3IiLCJnZXRFbGVtZW50c0J5VGFnTmFtZSIsIlBsYWNlaG9sZGVySW1nIiwiYXJnIiwic3ZnIiwicGxhY2Vob2xkZXJTVkdzIiwiZGVmYXVsdCIsImg1cEltYWdlRGVmYXVsdCIsIlJlc3VsdFNjcmVlbiIsInJlc3VsdFNjcmVlbiIsImhlYWRlciIsInNjb3JlSGVhZGVyIiwicXVlc3Rpb25Hcm91cHMiLCJncm91cCIsImdyb3VwQ29udGFpbmVyIiwibGlzdEhlYWRlcnMiLCJyZXN1bHRMaXN0IiwicXVlc3Rpb25zIiwicXVlc3Rpb24iLCJjcmVhdGVRdWVzdGlvbiIsImxpc3RJdGVtIiwiaW1nVXJsIiwidXNlRGVmYXVsdEltZyIsImltYWdlQ29udGFpbmVyIiwiQ29tcG9uZW50cyIsInF1ZXN0aW9uQ29udGFpbmVyIiwidXNlckFuc3dlciIsImFuc3dlckNvbnRhaW5lciIsImFuc3dlciIsImlzQ29ycmVjdCIsImNvcnJlY3RBbnN3ZXIiLCJzb2x1dGlvbkNvbnRhaW5lciIsImNvcnJlY3RBbnN3ZXJQcmVwZW5kIiwicG9pbnRzIl0sInNvdXJjZVJvb3QiOiIifQ==