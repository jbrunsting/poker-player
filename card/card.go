package card

import (
	"crypto/rand"
	"fmt"
	"math/big"
	"strings"
)

type Card struct {
	Suit int
	Val  int
}

const (
	MinVal      = 2
	MaxVal      = 14
	AceVal      = 14
	AceLowVal   = 1
	NumSuits    = 4
	SuitIndices = "shdc"
)

func CardsStr(cards []Card) string {
	if len(cards) == 0 {
		return ""
	}
	cardStrs := []string{}
	for _, c := range cards {
		cardStrs = append(cardStrs, c.String())
	}
	return fmt.Sprintf("%s ", strings.Join(cardStrs, " "))
}

func (c Card) String() string {
	unicode_card := int('🂠')
	if c.Val <= 10 {
		unicode_card += c.Val
	} else if c.Val == 11 {
		unicode_card += 11
	} else if c.Val == 12 {
		unicode_card += 13
	} else if c.Val == 13 {
		unicode_card += 14
	} else if c.Val == 14 {
		unicode_card++
	}
	unicode_card += c.Suit * 16
	return string(rune(unicode_card))
}

func (c *Card) Rank() int {
	return NumSuits*MaxVal + c.Suit
}

type Deck struct {
	cards  []Card
	length int
}

func (d *Deck) Init() {
	d.cards = []Card{}
	for s := 0; s < NumSuits; s++ {
		for i := MinVal; i <= MaxVal; i++ {
			d.cards = append(d.cards, Card{s, i})
		}
	}
	d.length = len(d.cards)
}

func swap(arr []Card, a int, b int) {
	arr[a], arr[b] = arr[b], arr[a]
}

// Removes the card permenantly, doesn't come back on reshuffle
func (d *Deck) Remove(cards []Card) {
	for _, toRemove := range cards {
		for i := 0; i < d.length; i++ {
			if toRemove == d.cards[i] {
				d.length -= 1
				swap(d.cards, i, d.length)
				d.cards = d.cards[:d.length]
				break
			}
		}
	}
}

func (d *Deck) Reshuffle() {
	d.length = len(d.cards)
}

func (d *Deck) Pop() Card {
	d.length -= 1
	if d.length < 0 {
		panic("Deck empty")
	}
	nBig, err := rand.Int(rand.Reader, big.NewInt(int64(d.length)))
	if err != nil {
		panic(err)
	}
	i := int(nBig.Int64())
	swap(d.cards, i, d.length)
	return d.cards[d.length]
}

func PadWithDeck(cards []Card, desiredLen int, d *Deck) []Card {
	for len(cards) < desiredLen {
		cards = append(cards, d.Pop())
	}
	return cards
}

func HasCard(cards []Card, val int) bool {
	for _, c := range cards {
		if c.Val == val {
			return true
		}
	}
	return false
}
