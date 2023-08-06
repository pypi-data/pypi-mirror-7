# -*- coding: spec -*-
# This is a comparison of DSL syntax to what is generated

import nose
import nose.tools
from sure import expect, this

import json
from noseOfYeti.tokeniser.support import noy_sup_setUp
from unittest import TestCase
import nose

import pkg_resources
import python_jsonschema_objects as pjs

describe TestCase, 'markdown extraction':

    before_each:
        md = pkg_resources.resource_filename('python_jsonschema_objects',
                '../README.md')
        self.examples = pjs.markdown_support.extract_code_blocks(md)
        self.example = json.loads(self.examples['schema'][0])

    it 'loads schema files':
        self.examples.should.have.key('schema')

    describe 'ObjectBuilder':

        it 'should be able to read an object':
            examples = map(json.loads, self.examples['schema'])
            for ex in examples:
                builder = pjs.ObjectBuilder(ex)
                builder.should.be.ok

        it 'should be able to build classes':
            examples = map(json.loads, self.examples['schema'])
            for ex in examples:
                builder = pjs.ObjectBuilder(self.example)
                builder.should.be.ok
                namespace = builder.build_classes()
                this(namespace).should.be.ok

        context 'PersonExample':
            before_each:
                self.builder = pjs.ObjectBuilder(self.example)
                namespace = self.builder.build_classes()
                self.Person = namespace.ExampleSchema

            it 'should allow empty objects':
                person = self.Person()
                person.should.be.ok

            it 'should allow attributes to be given':
                person = self.Person(firstName="James",
                        lastName="Bond", age=35)
                str(person.firstName).should.equal("James")
                str(person.lastName).should.equal("Bond")
                int(person.age).should.equal(35)
                person.should.be.ok

            it 'should allow non-required attributes to be missing':
                person = self.Person(firstName="James",
                        lastName="Bond")
                person.should.be.ok
                str(person.firstName).should.equal("James")
                str(person.lastName).should.equal("Bond")

            it 'should not allow required attributes to be missing':
                self.Person.when.called_with(firstName="James").should.throw(
                        pjs.ValidationError
                        )

            it 'should validate minimum age':
                self.Person.when.called_with(
                        firstName="James", lastName="Bond",
                        age=-10).should.throw(pjs.ValidationError)

                person = self.Person(firstName="James",
                        lastName="Bond")

                def setage(x):
                    person.age = x

                setage.when.called_with(-1).should.throw(pjs.ValidationError)

            it 'should validate before serializing':
                person = self.Person(firstName="James",
                        lastName="Bond")

                person._properties['age'] = -1

                person.serialize.when.called_with().should.throw(pjs.ValidationError)

            it 'should remove null values when serializing':
                person = self.Person(firstName="James",
                        lastName="Bond")

                json_str = person.serialize()
                json.loads(json_str).should_not.have.key('age')

            it 'should serialize lists':
                person = self.Person(
                        firstName="James",
                        lastName="Bond",
                        dogs=["Lassie", "Bobo"]
                        )

                json_str = person.serialize()
                json.loads(json_str).should.equal(
                    {
                      'firstName': "James",
                      'lastName': "Bond",
                      'dogs': ["Lassie", "Bobo"]
                      }
                    )

            it 'should transform into dictionaries recursively"':
                pdict = dict(
                        firstName="James",
                        lastName="Bond",
                        dogs=["Lassie", "Bobo"]
                        )

                person = self.Person( **pdict)

                person.as_dict().should.equal(pdict)
