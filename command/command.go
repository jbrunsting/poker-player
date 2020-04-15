package command

import (
	"fmt"
	"strconv"
	"strings"

	"github.com/jbrunsting/poker-player/card"
)

type ParamType int

const (
	CardParam = iota
	StringParam
	NumberParam
)

type Param struct {
	Kind   ParamType
	Card   *card.Card
	String string
	Number int
}

type Command struct {
	Name       string
	ParamTypes []ParamType
	Fn         func([]Param)
}

func cardInput(input string) (card.Card, error) {
	c := card.Card{}
	if len(input) == 2 || len(input) == 3 {
		c.Suit = strings.IndexByte(card.SuitIndices, input[len(input)-1])
		if !(0 <= c.Suit && c.Suit <= card.NumSuits) {
			return c, fmt.Errorf("Card suit out of range")
		}

		valInput := input[:len(input)-1]
		if valInput == "j" {
			c.Val = 11
		} else if valInput == "q" {
			c.Val = 12
		} else if valInput == "k" {
			c.Val = 13
		} else if valInput == "a" {
			c.Val = 14
		} else {
			val, err := strconv.Atoi(valInput)
			if err != nil {
				return c, err
			}
			if !(card.MinVal <= val && val <= card.MaxVal) {
				return c, fmt.Errorf("Card value out of range")
			}
			c.Val = val
		}
	}
	return c, nil
}

func (c Command) String() string {
	return c.Name
}

func (c *Command) Parse(input string) bool {
	components := strings.Fields(input)
	if len(components) == 0 || components[0] != c.Name {
		return false
	}
	components = components[1:]

	results := []Param{}
	for _, kind := range c.ParamTypes {
		if len(components) == 0 {
			return false
		}

		p := Param{}
		p.Kind = kind
		if kind == CardParam {
			c, err := cardInput(components[0])
			if err != nil {
				return false
			}
			p.Card = &c
		} else if kind == StringParam {
			p.String = components[0]
		} else if kind == NumberParam {
			i, err := strconv.Atoi(components[0])
			if err != nil {
				return false
			}
			p.Number = i
		}
		results = append(results, p)
		components = components[1:]
	}
	c.Fn(results)
	return true
}
