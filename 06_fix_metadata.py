import nixio as nix
import argparse
import os
from IPython import embed
import numpy as np


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def find_section(nix_file, pattern, case_sensitive=False, full_match=False):
    def type_lambda(typ, full_match):
        if full_match:
            return lambda s: typ.lower() == s.type.lower()
        else:
            return lambda s: typ.lower() in s.type.lower()

    def name_lambda(name, full_match):
        if full_match:
            return lambda s: name.lower() == s.name.lower()
        else:
            return lambda s: name.lower() in s.name.lower()

    def name_lambda_cs(name, full_match):
        if full_match:
            return lambda s: name == s.name
        else:
            return lambda s: name in s.name

    secs = nix_file.find_sections(type_lambda(pattern, full_match))
    if len(secs) == 0:
        secs = nix_file.find_sections(name_lambda_cs(pattern, full_match) if case_sensitive
                                      else name_lambda(pattern, full_match))
    return secs


def find_property(nix_file, pattern, case_sensitive=False, full_match=False):
    name = pattern if case_sensitive else pattern.lower()
    props = {}
    for sec in nix_file.find_sections(lambda s: True):
        for prop in sec.props:
            pname = prop.name if case_sensitive else prop.name.lower()
            if name == pname if full_match else name in pname:
                if sec not in props.keys():
                    props[sec] = []
                props[sec].append(prop)
    return props


def filter_props(props, args):
    new_props = {}
    for k in props.keys():
        if k.name == args.section:
            new_props[k] = props[k]
    return new_props


def fix_property(args):
    nix_file = nix.File.open(args.file, nix.FileMode.ReadWrite)
    b = nix_file.blocks[0]
    props = find_property(nix_file, args.property, True, True)
    props = filter_props(props, args)

    if len(props.keys()) > 1:
        nix_file.close()
        raise ValueError("Property name %s is not unique! Exiting!" % args.property)
    
    if len(props.keys()) == 0:
        if args.add_property:
            if len(args.section.strip()) > 0:
                secs = find_section(nix_file, args.section, True, True)
                if len(secs) > 0:
                    s = secs[-1]
                else:
                    s = b.metadata.create_section(args.section, args.section)
            else:
                s = b.metadata                        
            if is_number(args.value):
                v = nix.Value(float(args.value))
                p = s.create_property(args.property, nix.Value(float(args.value)))
                if len(args.unit.strip()) > 0:
                    p.unit = args.unit
            else:
                s[args.property] = args.value
        else:
            print("Property %s was not found!" % args.property)
    else:
        p = props[list(props.keys())[0]][0]
        p.delete_values()

        if is_number(args.value):
            if p.data_type == np.bytes_:
                p.values = [nix.Value(args.value)]
            else:
                v = nix.Value(float(args.value))
                p.values = [v]
            if len(args.unit.strip()) > 0:             
                p.unit = args.unit
        else:
            p.values = [nix.Value(args.value)]
    nix_file.close()


def create_parser():
    parser = argparse.ArgumentParser(description="Fix metadata settings in nix files. To change, for example, the comment use: fix_metadata 'Comment' 'new comment', if the metadata does not contain the field, a new property will be created on global level. NOTE: field names are case sensitive!")
    parser.add_argument("file", type=str, help="nix-file that needs some fixing.")
    parser.add_argument("property", type=str, help="The name of the property.")
    parser.add_argument("value", type=str, help="The new value")
    parser.add_argument("-u", "--unit", type=str, default="", help="The unit of the value. Must be an SI unit!")
    parser.add_argument("-a", "--add_property", action="store_true", help="Adds the property, it not found.")
    parser.add_argument("-s", "--section", type=str, default="", help="the section in which a property should be found.")
    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()
    if not os.path.exists(args.file):
        raise ValueError("The file %s does not exist!" % args.file)
    fix_property(args)


if __name__== "__main__":
    main()