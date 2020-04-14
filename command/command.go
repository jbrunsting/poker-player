package command

import (
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
			p.Card = &card.Card{}
//			c = card_input(components[0])
//			if c == nil {
//				break
//			}
//			results = append(results, c)
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
