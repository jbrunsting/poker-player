package card

import (
	"fmt"
	"strings"
)

type Card struct {
	Suit int
	Val  int
}

const (
	MinVal      = 2
	MaxVal      = 14
	NumSuits    = 4
	SuitIndices = "shdc"
)

func CardsStr(cards []Card) string {
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
