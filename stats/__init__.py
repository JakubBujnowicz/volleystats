#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def attack_eff(kills, errors, blocked, total):
    return (kill - errors - blocked) / total

def serve_eff(aces, slashes, errors, total,
              slash_mult=1):
    return (aces + slash_mult * slashes - errors) / total
