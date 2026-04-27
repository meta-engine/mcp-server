import { Id } from '../../../shared/value-objects/Id';

/** CartLine value object */
export interface CartLine {
  readonly productId: Id;
  readonly quantity: number;
}
