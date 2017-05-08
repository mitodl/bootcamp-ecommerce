declare type ElementEventTemplate<E> = {
  target: E
} & Event;

export type InputEvent = ElementEventTemplate<HTMLInputElement>;
