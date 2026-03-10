/**
 * Mobile Utility Functions Tests
 *
 * Tests for mobile-specific utility functions including:
 * - Safe area detection
 * - Viewport management
 * - Touch detection
 * - Platform detection
 * - Gesture handlers
 */

// @ts-nocheck
import { describe, it, expect, beforeEach, afterEach, vi, type Mock } from 'vitest';
import {
  getSafeAreaBottom,
  getSafeAreaTop,
  hasNotch,
  lockViewportHeight,
  getViewportHeight,
  isTouchDevice,
  prefersReducedMotion,
  createSwipeHandlers,
  hasHardwareKeyboard,
  isIOS,
  isAndroid,
  isMobile,
  hideKeyboard,
  scrollIntoViewWithOffset,
  preventScrollPropagation,
} from '../mobile';

// Mock window and document
const mockWindow = {
  innerHeight: 800,
  addEventListener: vi.fn(),
  removeEventListener: vi.fn(),
  matchMedia: vi.fn(),
};

const mockDocument = {
  documentElement: {
    style: {
      getPropertyValue: vi.fn(),
      setProperty: vi.fn(),
    },
  },
  activeElement: null,
};

Object.defineProperty(global, 'window', {
  value: mockWindow,
  writable: true,
});

Object.defineProperty(global, 'document', {
  value: mockDocument,
  writable: true,
});

Object.defineProperty(global, 'navigator', {
  value: {
    maxTouchPoints: 0,
    userAgent: '',
    platform: '',
  },
  writable: true,
});

describe('Safe Area Utilities', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('getSafeAreaBottom', () => {
    it('should return 0 when window is undefined', () => {
      Object.defineProperty(global, 'window', { value: undefined, writable: true });
      expect(getSafeAreaBottom()).toBe(0);
      Object.defineProperty(global, 'window', { value: mockWindow, writable: true });
    });

    it('should return safe area bottom when set', () => {
      mockDocument.documentElement.style.getPropertyValue.mockReturnValue('34px');
      expect(getSafeAreaBottom()).toBe(34);
    });

    it('should return 0 when safe area is not set', () => {
      mockDocument.documentElement.style.getPropertyValue.mockReturnValue('');
      expect(getSafeAreaBottom()).toBe(0);
    });
  });

  describe('getSafeAreaTop', () => {
    it('should return 0 when window is undefined', () => {
      Object.defineProperty(global, 'window', { value: undefined, writable: true });
      expect(getSafeAreaTop()).toBe(0);
      Object.defineProperty(global, 'window', { value: mockWindow, writable: true });
    });

    it('should return safe area top when set', () => {
      mockDocument.documentElement.style.getPropertyValue.mockReturnValue('44px');
      expect(getSafeAreaTop()).toBe(44);
    });
  });

  describe('hasNotch', () => {
    it('should return true when bottom safe area exists', () => {
      mockDocument.documentElement.style.getPropertyValue.mockImplementation((prop) => {
        if (prop === 'safe-area-inset-bottom') return '34px';
        return '0px';
      });
      expect(hasNotch()).toBe(true);
    });

    it('should return true when top safe area exists', () => {
      mockDocument.documentElement.style.getPropertyValue.mockImplementation((prop) => {
        if (prop === 'safe-area-inset-top') return '44px';
        return '0px';
      });
      expect(hasNotch()).toBe(true);
    });

    it('should return false when no safe areas', () => {
      mockDocument.documentElement.style.getPropertyValue.mockReturnValue('0px');
      expect(hasNotch()).toBe(false);
    });
  });
});

describe('Viewport Management', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockWindow.innerHeight = 800;
  });

  describe('lockViewportHeight', () => {
    it('should set CSS custom property for viewport height', () => {
      const cleanup = lockViewportHeight();

      expect(mockDocument.documentElement.style.setProperty).toHaveBeenCalledWith(
        '--vh',
        '8px'
      ); // 800 * 0.01 = 8

      cleanup();
    });

    it('should add resize event listener', () => {
      const cleanup = lockViewportHeight();

      expect(mockWindow.addEventListener).toHaveBeenCalledWith('resize', expect.any(Function));
      expect(mockWindow.addEventListener).toHaveBeenCalledWith('orientationchange', expect.any(Function));

      cleanup();
    });

    it('should return cleanup function that removes listeners', () => {
      const cleanup = lockViewportHeight();

      cleanup();

      expect(mockWindow.removeEventListener).toHaveBeenCalledWith('resize', expect.any(Function));
      expect(mockWindow.removeEventListener).toHaveBeenCalledWith('orientationchange', expect.any(Function));
    });

    it('should return empty function when window is undefined', () => {
      Object.defineProperty(global, 'window', { value: undefined, writable: true });

      const cleanup = lockViewportHeight();
      expect(typeof cleanup).toBe('function');

      Object.defineProperty(global, 'window', { value: mockWindow, writable: true });
    });
  });

  describe('getViewportHeight', () => {
    it('should return calculated height from CSS variable', () => {
      mockDocument.documentElement.style.getPropertyValue.mockReturnValue('8px');
      expect(getViewportHeight()).toBe(800);
    });

    it('should return window.innerHeight when CSS variable not set', () => {
      mockDocument.documentElement.style.getPropertyValue.mockReturnValue('');
      expect(getViewportHeight()).toBe(800);
    });

    it('should return 0 when window is undefined', () => {
      Object.defineProperty(global, 'window', { value: undefined, writable: true });
      expect(getViewportHeight()).toBe(0);
      Object.defineProperty(global, 'window', { value: mockWindow, writable: true });
    });
  });
});

describe('Touch Detection', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    (navigator as any).maxTouchPoints = 0;
  });

  describe('isTouchDevice', () => {
    it('should return true when ontouchstart exists', () => {
      Object.defineProperty(mockWindow, 'ontouchstart', { value: vi.fn(), writable: true });
      expect(isTouchDevice()).toBe(true);
      delete mockWindow.ontouchstart;
    });

    it('should return true when maxTouchPoints > 0', () => {
      (navigator as any).maxTouchPoints = 5;
      expect(isTouchDevice()).toBe(true);
      (navigator as any).maxTouchPoints = 0;
    });

    it('should return false when no touch support', () => {
      expect(isTouchDevice()).toBe(false);
    });

    it('should return false when window is undefined', () => {
      Object.defineProperty(global, 'window', { value: undefined, writable: true });
      expect(isTouchDevice()).toBe(false);
      Object.defineProperty(global, 'window', { value: mockWindow, writable: true });
    });
  });

  describe('prefersReducedMotion', () => {
    it('should return true when prefers-reduced-motion is set', () => {
      mockWindow.matchMedia.mockReturnValue({ matches: true });
      expect(prefersReducedMotion()).toBe(true);
    });

    it('should return false when prefers-reduced-motion is not set', () => {
      mockWindow.matchMedia.mockReturnValue({ matches: false });
      expect(prefersReducedMotion()).toBe(false);
    });
  });
});

describe('Gesture Detection', () => {
  describe('createSwipeHandlers', () => {
    it('should detect swipe right', () => {
      const onSwipeRight = vi.fn();
      const { onTouchStart, onTouchEnd } = createSwipeHandlers({ onSwipeRight });

      const startEvent = {
        changedTouches: [{ screenX: 100, screenY: 100 }],
      } as any;

      const endEvent = {
        changedTouches: [{ screenX: 200, screenY: 100 }],
      } as any;

      onTouchStart(startEvent);
      onTouchEnd(endEvent);

      expect(onSwipeRight).toHaveBeenCalled();
    });

    it('should detect swipe left', () => {
      const onSwipeLeft = vi.fn();
      const { onTouchStart, onTouchEnd } = createSwipeHandlers({ onSwipeLeft });

      const startEvent = {
        changedTouches: [{ screenX: 200, screenY: 100 }],
      } as any;

      const endEvent = {
        changedTouches: [{ screenX: 100, screenY: 100 }],
      } as any;

      onTouchStart(startEvent);
      onTouchEnd(endEvent);

      expect(onSwipeLeft).toHaveBeenCalled();
    });

    it('should detect swipe up', () => {
      const onSwipeUp = vi.fn();
      const { onTouchStart, onTouchEnd } = createSwipeHandlers({ onSwipeUp });

      const startEvent = {
        changedTouches: [{ screenX: 100, screenY: 200 }],
      } as any;

      const endEvent = {
        changedTouches: [{ screenX: 100, screenY: 100 }],
      } as any;

      onTouchStart(startEvent);
      onTouchEnd(endEvent);

      expect(onSwipeUp).toHaveBeenCalled();
    });

    it('should detect swipe down', () => {
      const onSwipeDown = vi.fn();
      const { onTouchStart, onTouchEnd } = createSwipeHandlers({ onSwipeDown });

      const startEvent = {
        changedTouches: [{ screenX: 100, screenY: 100 }],
      } as any;

      const endEvent = {
        changedTouches: [{ screenX: 100, screenY: 200 }],
      } as any;

      onTouchStart(startEvent);
      onTouchEnd(endEvent);

      expect(onSwipeDown).toHaveBeenCalled();
    });

    it('should detect tap', () => {
      const onTap = vi.fn();
      const { onTouchStart, onTouchEnd } = createSwipeHandlers({ onTap });

      const startEvent = {
        changedTouches: [{ screenX: 100, screenY: 100 }],
      } as any;

      const endEvent = {
        changedTouches: [{ screenX: 105, screenY: 102 }],
      } as any;

      onTouchStart(startEvent);
      onTouchEnd(endEvent);

      expect(onTap).toHaveBeenCalled();
    });

    it('should respect custom threshold', () => {
      const onSwipeRight = vi.fn();
      const { onTouchStart, onTouchEnd } = createSwipeHandlers({
        onSwipeRight,
        threshold: 100,
      });

      const startEvent = {
        changedTouches: [{ screenX: 100, screenY: 100 }],
      } as any;

      const endEvent = {
        changedTouches: [{ screenX: 150, screenY: 100 }],
      } as any;

      onTouchStart(startEvent);
      onTouchEnd(endEvent);

      // Should not trigger because distance (50) < threshold (100)
      expect(onSwipeRight).not.toHaveBeenCalled();
    });
  });
});

describe('Keyboard Detection', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('hasHardwareKeyboard', () => {
    it('should return true on large screens', () => {
      mockWindow.matchMedia.mockReturnValue({ matches: true });
      expect(hasHardwareKeyboard()).toBe(true);
    });

    it('should return false on small screens', () => {
      mockWindow.matchMedia.mockReturnValue({ matches: false });
      expect(hasHardwareKeyboard()).toBe(false);
    });
  });
});

describe('Platform Detection', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    (navigator as any).maxTouchPoints = 0;
  });

  describe('isIOS', () => {
    it('should detect iPhone', () => {
      (navigator as any).userAgent = 'iPhone';
      expect(isIOS()).toBe(true);
    });

    it('should detect iPad', () => {
      (navigator as any).userAgent = 'iPad';
      expect(isIOS()).toBe(true);
    });

    it('should detect iPod', () => {
      (navigator as any).userAgent = 'iPod';
      expect(isIOS()).toBe(true);
    });

    it('should detect iOS Mac with touch', () => {
      (navigator as any).userAgent = '';
      (navigator as any).platform = 'MacIntel';
      (navigator as any).maxTouchPoints = 5;
      expect(isIOS()).toBe(true);
    });

    it('should return false for non-iOS', () => {
      (navigator as any).userAgent = 'Android';
      (navigator as any).platform = 'Win32';
      expect(isIOS()).toBe(false);
    });
  });

  describe('isAndroid', () => {
    it('should detect Android', () => {
      (navigator as any).userAgent = 'Android';
      expect(isAndroid()).toBe(true);
    });

    it('should return false for non-Android', () => {
      (navigator as any).userAgent = 'iPhone';
      expect(isAndroid()).toBe(false);
    });
  });

  describe('isMobile', () => {
    it('should return true for iOS', () => {
      (navigator as any).userAgent = 'iPhone';
      expect(isMobile()).toBe(true);
    });

    it('should return true for Android', () => {
      (navigator as any).userAgent = 'Android';
      expect(isMobile()).toBe(true);
    });

    it('should return false for desktop', () => {
      (navigator as any).userAgent = '';
      (navigator as any).platform = 'Win32';
      expect(isMobile()).toBe(false);
    });
  });
});

describe('Input Mode Utilities', () => {
  describe('hideKeyboard', () => {
    it('should blur active element', () => {
      const mockElement = { blur: vi.fn() };
      mockDocument.activeElement = mockElement;

      hideKeyboard();

      expect(mockElement.blur).toHaveBeenCalled();
    });

    it('should handle null active element', () => {
      mockDocument.activeElement = null;

      expect(() => hideKeyboard()).not.toThrow();
    });

    it('should handle undefined document', () => {
      Object.defineProperty(global, 'document', { value: undefined, writable: true });
      expect(() => hideKeyboard()).not.toThrow();
      Object.defineProperty(global, 'document', { value: mockDocument, writable: true });
    });
  });
});

describe('Scroll Utilities', () => {
  beforeEach(() => {
    mockWindow.pageYOffset = 0;
    mockWindow.scrollTo = vi.fn();
  });

  describe('scrollIntoViewWithOffset', () => {
    it('should scroll element into view with offset', () => {
      const mockElement = {
        getBoundingClientRect: vi.fn().mockReturnValue({ top: 200 }),
      } as any;

      scrollIntoViewWithOffset(mockElement, 80);

      expect(mockWindow.scrollTo).toHaveBeenCalledWith({
        top: 120,
        behavior: 'smooth',
      });
    });

    it('should use default offset of 80', () => {
      const mockElement = {
        getBoundingClientRect: vi.fn().mockReturnValue({ top: 300 }),
      } as any;

      scrollIntoViewWithOffset(mockElement);

      expect(mockWindow.scrollTo).toHaveBeenCalledWith({
        top: 220,
        behavior: 'smooth',
      });
    });
  });

  describe('preventScrollPropagation', () => {
    it('should prevent default when at top and scrolling up', () => {
      const container = {
        scrollTop: 0,
        clientHeight: 500,
        scrollHeight: 1000,
      } as any;

      const event = {
        deltaY: -10,
        currentTarget: container,
        preventDefault: vi.fn(),
      } as any;

      preventScrollPropagation(event);

      expect(event.preventDefault).toHaveBeenCalled();
    });

    it('should prevent default when at bottom and scrolling down', () => {
      const container = {
        scrollTop: 500,
        clientHeight: 500,
        scrollHeight: 1000,
      } as any;

      const event = {
        deltaY: 10,
        currentTarget: container,
        preventDefault: vi.fn(),
      } as any;

      preventScrollPropagation(event);

      expect(event.preventDefault).toHaveBeenCalled();
    });

    it('should not prevent default in middle of scroll', () => {
      const container = {
        scrollTop: 250,
        clientHeight: 500,
        scrollHeight: 1000,
      } as any;

      const event = {
        deltaY: 10,
        currentTarget: container,
        preventDefault: vi.fn(),
      } as any;

      preventScrollPropagation(event);

      expect(event.preventDefault).not.toHaveBeenCalled();
    });
  });
});
