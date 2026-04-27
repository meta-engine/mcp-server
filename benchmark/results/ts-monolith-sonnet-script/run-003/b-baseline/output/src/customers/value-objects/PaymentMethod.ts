import { PaymentMethodKind } from '../enums/PaymentMethodKind';

/** PaymentMethod value object */
export interface PaymentMethod {
  readonly kind: PaymentMethodKind;
  readonly lastFour: string;
}
