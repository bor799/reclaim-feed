/**
 * Mobile-First Utility Functions
 * Touch gestures, safe area handling, and viewport management
 */

// ============ Safe Area Utilities ============

/**
 * Get the safe area inset bottom value (for notched devices)
 */
export function getSafeAreaBottom(): number {
    if (typeof window === 'undefined') return 0;

    const style = getComputedStyle(document.documentElement);
    const bottom = style.getPropertyValue('safe-area-inset-bottom');
    return parseInt(bottom, 10) || 0;
}

/**
 * Get the safe area inset top value (for notched devices)
 */
export function getSafeAreaTop(): number {
    if (typeof window === 'undefined') return 0;

    const style = getComputedStyle(document.documentElement);
    const top = style.getPropertyValue('safe-area-inset-top');
    return parseInt(top, 10) || 0;
}

/**
 * Check if device has a notch
 */
export function hasNotch(): boolean {
    if (typeof window === 'undefined') return false;
    return getSafeAreaBottom() > 0 || getSafeAreaTop() > 0;
}

// ============ Viewport Management ============

/**
 * Lock viewport height to prevent mobile browser chrome issues
 * Sets CSS custom property for visual viewport height
 */
export function lockViewportHeight(): () => void {
    if (typeof window === 'undefined') return () => {};

    const setVH = () => {
        const vh = window.innerHeight * 0.01;
        document.documentElement.style.setProperty('--vh', `${vh}px`);
    };

    setVH();
    window.addEventListener('resize', setVH);
    window.addEventListener('orientationchange', setVH);

    return () => {
        window.removeEventListener('resize', setVH);
        window.removeEventListener('orientationchange', setVH);
    };
}

/**
 * Get the locked viewport height in pixels
 */
export function getViewportHeight(): number {
    if (typeof window === 'undefined') return 0;

    const vh = parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--vh'));
    return vh ? vh * 100 : window.innerHeight;
}

// ============ Touch Detection ============

/**
 * Check if device supports touch
 */
export function isTouchDevice(): boolean {
    if (typeof window === 'undefined') return false;

    return (
        'ontouchstart' in window ||
        navigator.maxTouchPoints > 0 ||
        // @ts-expect-error - msMaxTouchPoints is IE specific
        navigator.msMaxTouchPoints > 0
    );
}

/**
 * Check if user prefers reduced motion
 */
export function prefersReducedMotion(): boolean {
    if (typeof window === 'undefined') return false;

    return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
}

// ============ Gesture Detection ============

export interface SwipeCallbacks {
    onSwipeLeft?: () => void;
    onSwipeRight?: () => void;
    onSwipeUp?: () => void;
    onSwipeDown?: () => void;
    onTap?: () => void;
    threshold?: number;
}

/**
 * Create touch event handlers for swipe gestures
 */
export function createSwipeHandlers(callbacks: SwipeCallbacks) {
    const {
        onSwipeLeft,
        onSwipeRight,
        onSwipeUp,
        onSwipeDown,
        onTap,
        threshold = 50
    } = callbacks;

    let touchStartX = 0;
    let touchStartY = 0;
    let touchEndX = 0;
    let touchEndY = 0;

    const minSwipeDistance = threshold;

    const onTouchStart = (e: React.TouchEvent) => {
        touchStartX = e.changedTouches[0].screenX;
        touchStartY = e.changedTouches[0].screenY;
    };

    const onTouchEnd = (e: React.TouchEvent) => {
        touchEndX = e.changedTouches[0].screenX;
        touchEndY = e.changedTouches[0].screenY;
        handleGesture();
    };

    const handleGesture = () => {
        const deltaX = touchEndX - touchStartX;
        const deltaY = touchEndY - touchStartY;

        // Check if it's a tap (minimal movement)
        if (Math.abs(deltaX) < 10 && Math.abs(deltaY) < 10) {
            onTap?.();
            return;
        }

        // Determine if horizontal or vertical swipe
        if (Math.abs(deltaX) > Math.abs(deltaY)) {
            // Horizontal swipe
            if (Math.abs(deltaX) > minSwipeDistance) {
                if (deltaX > 0) {
                    onSwipeRight?.();
                } else {
                    onSwipeLeft?.();
                }
            }
        } else {
            // Vertical swipe
            if (Math.abs(deltaY) > minSwipeDistance) {
                if (deltaY > 0) {
                    onSwipeDown?.();
                } else {
                    onSwipeUp?.();
                }
            }
        }
    };

    return { onTouchStart, onTouchEnd };
}

// ============ Keyboard Detection ============

/**
 * Check if hardware keyboard is likely attached
 */
export function hasHardwareKeyboard(): boolean {
    if (typeof window === 'undefined') return false;

    // Large screen typically means desktop with keyboard
    return window.matchMedia('(min-width: 1024px)').matches;
}

// ============ Platform Detection ============

/**
 * Check if running on iOS
 */
export function isIOS(): boolean {
    if (typeof window === 'undefined') return false;

    return /iPad|iPhone|iPod/.test(navigator.userAgent) ||
        (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
}

/**
 * Check if running on Android
 */
export function isAndroid(): boolean {
    if (typeof window === 'undefined') return false;

    return /Android/.test(navigator.userAgent);
}

/**
 * Check if running on mobile device
 */
export function isMobile(): boolean {
    return isIOS() || isAndroid();
}

// ============ Input Mode Utilities ============

/**
 * Hide virtual keyboard (works on some mobile browsers)
 */
export function hideKeyboard(): void {
    if (typeof document === 'undefined') return;

    // Blur active element
    if (document.activeElement instanceof HTMLElement) {
        document.activeElement.blur();
    }
}

// ============ Scroll Utilities ============

/**
 * Scroll element into view with offset for fixed headers
 */
export function scrollIntoViewWithOffset(element: HTMLElement, offset = 80): void {
    const elementPosition = element.getBoundingClientRect().top;
    const offsetPosition = elementPosition + window.pageYOffset - offset;

    window.scrollTo({
        top: offsetPosition,
        behavior: 'smooth'
    });
}

/**
 * Prevent scroll propagation (useful for nested scroll containers)
 */
export function preventScrollPropagation(e: React.WheelEvent): void {
    const container = e.currentTarget;
    const isScrollingUp = e.deltaY < 0;

    const isAtTop = container.scrollTop === 0;
    const isAtBottom = container.scrollTop + container.clientHeight >= container.scrollHeight;

    if ((isAtTop && isScrollingUp) || (isAtBottom && !isScrollingUp)) {
        e.preventDefault();
    }
}
