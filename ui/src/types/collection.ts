import { Card } from "./card"

export type Collection = {
  id: number
  name: string
  amount_of_cards: number
}

export type CollectionWithCards = Collection & {cards: Card[]}