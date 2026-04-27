/** State of a shipment in the fulfillment pipeline. */
export enum ShipmentState {
  Pending = 0,
  InTransit = 1,
  Delivered = 2,
  Lost = 3,
}
